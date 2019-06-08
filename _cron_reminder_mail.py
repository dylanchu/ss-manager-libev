#!/usr/bin/python3
# -*- coding: utf-8 -*-

import config
from database import Database as db
import datetime
import smtplib
from email.mime.text import MIMEText

template = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body>
  <p>亲爱的 {user}：</p>
  <p>您的ss proxy套餐 '{plan_type}' 将在 {end_time} 到期, 请及时续费以免影响正常使用~ 
  如您到期未续费, 系统将自动关停服务....
  <br>如您已联系管理员续费, 请忽略这封邮件 !
  <br><small>> 该邮件由系统自动发出, 如您由任何疑问, 可直接恢复该邮件或微信联系管理员.<br></small></p>
  <p>谢谢
  <br>❄ssmanev-libev<br><small>发送于 '{now}'.</small></p>
</body></html>'''

template2 = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body>
  <p> '{user}'（注册邮箱：{mailaddr}）<br>的套餐 '{plan_type}' 将在 {end_time} 到期，已尝试发送邮件提醒。
  <br><small>该邮件发送于 '{now}'.</small></p>
</body></html>'''


def mailto(recipient, subject, content):
    if recipient == '' or subject == '' or content == '':
        print("ERROR: '%s' '%s' '%s'" % (recipient, subject, content))
        return
        # raise Exception('all 3 arguments should not be empty')
    else:
        # if not isinstance(subject, unicode):
        #     subject = unicode(subject)
        msg = MIMEText(content, 'html', 'utf-8')    # 'plain' or 'html'
        msg["Accept-Language"] = "zh-CN"
        msg["Accept-Charset"] = "ISO-8859-1,utf-8"
        msg['From'] = config.MAIL_FROM
        msg['To'] = recipient
        msg['Subject'] = subject
        print(msg)
        try:
            # 这里需要SMTP_SSL，不是普通邮箱的SMTP
            smtp = smtplib.SMTP_SSL(config.MAIL_HOST, config.MAIL_PORT)
            smtp.login(config.MAIL_USER, config.MAIL_PASSWORD)
            smtp.sendmail(config.MAIL_FROM, recipient, msg.as_string())
            smtp.quit()
            print("send email success")
        except Exception as e:
            print("send email failed %s" % e)


def main():
    # only check paid users and only send emails exactly 3 days before plan end time
    var_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    var_nowf = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    var_today = datetime.date.today()
    print('===================================================  now: %s' % var_now)

    for name, email, plan, expire in db.get_users_reminder_mail():
        #        0        1        2           3
        #    user_name, email, plan_type, plan_end_time
        if not plan == 'free':
            diff = expire.date() - var_today
            diff_days = diff.total_seconds() / 86400
            if diff_days == 2:
                print('\n2天后到期 (user_name: %s) 将发送提醒邮件到 %s ...' % (name, email))
                content = template.format(user=name, plan_type=plan,
                                          end_time=expire.strftime('%Y-%m-%d %H:%M'), now=var_nowf)
                # send e-mail and make a copy to myself
                mailto(email, '到期提醒', content)
                content2 = template2.format(user=name, mailaddr=email, plan_type=plan,
                                            end_time=expire.strftime('%Y-%m-%d %H:%M'), now=var_nowf)
                mailto('support@exmail.peanut.ga', '自我备注：到期提醒', content2)
                print('\n')
            else:
                print('%d days  (user_name: %s)' % (diff_days, name))


if __name__ == '__main__':
    main()
