#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Database functions
import datetime
import cymysql
import config
from config import logger


class Database:
    @staticmethod
    def query(sql):
        try:
            conn = cymysql.connect(host=config.DB_HOST, port=config.DB_PORT, user=config.DB_USER, passwd=config.DB_PASSWORD,
                                   db=config.DB_NAME, charset='utf8')
            cur = conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            conn.commit()
            conn.close()
            return result
        except Exception as e:
            logger.error(e)

    @classmethod
    def get_all_users(cls):
        sql = 'SELECT id,email,ss_port,ss_enabled,level,traffic_up,traffic_down,' \
              'traffic_quota,plan_end_time FROM db_user;'
        return cls.query(sql)

    @classmethod
    def get_enabled_ports(cls):
        """return: dict, like {8001:'aaaa', 8002:'bbbb'}
        """
        result = {}
        sql = 'SELECT ss_port,ss_passwd FROM db_user WHERE ss_enabled=1;'
        temp = cls.query(sql)
        logger.debug('get enabled ports from db:')
        logger.debug(temp)
        for port, pwd in temp:
            if port:
                result.update({port: pwd})
        # for i in range(8001, 8006):    # only for test
        #    result.update({i: 'asdfasdfasdfasdfasdfasdf'})
        return result

    @classmethod
    def push_used_traffic(cls, traffics_to_add):
        """:param traffics_to_add: dict, like {8001: 1524892, 8002: 17382345}
        :return: None
        """
        if not traffics_to_add:
            return
        sql1 = "UPDATE db_user SET traffic_down=traffic_down+CASE ss_port"
        # sql2 = " WHEN 17009 THEN 990 WHEN 17011 THEN 90"
        sql2 = ''
        for p in traffics_to_add:
            sql2 = ''.join([sql2, ' WHEN ', str(p), ' THEN ', str(traffics_to_add[p])])
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # sql3 = " END, last_use_time='2222-2-22 22:22:22' WHERE ss_port IN (17009, 17011);"
        sql3 = " END, last_use_time='%s' WHERE ss_port IN (%s);" % (time_now, str(list(traffics_to_add))[1:-1])
        sql = ''.join([sql1, sql2, sql3])
        cls.query(sql)

    @classmethod
    def log_traffic_history(cls, traffics):
        """traffics: dict, like {8001: 28372, 8002: 186782}"""
        # +----+------+---------+----------+---------+
        # | id | uid  | ss_port | log_time | traffic |
        # +----+------+---------+----------+---------+
        if not traffics:
            return
        sql1 = "INSERT INTO db_traffic(ss_port,log_time,traffic) VALUES "
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql2 = ''
        for p in traffics:
            sql2 = ''.join([sql2, "(%d,'%s',%d)," % (p, time_now, traffics[p])])
        # Make sql and fill the corresponding user id (better create index on uid)
        sql = ''.join([sql1, sql2[0:-1], ';UPDATE db_traffic SET uid=(SELECT id FROM db_user '
                                         'WHERE ss_port=db_traffic.ss_port) WHERE uid IS NULL;'])
        cls.query(sql)

    @classmethod
    def disable_user(cls, ids):
        if not ids:
            return
        sql = "UPDATE db_user SET ss_enabled=0 WHERE id IN (%s)" % str(ids)[1:-1]
        cls.query(sql)

    @classmethod
    def enable_user(cls, ids):
        if not ids:
            return
        sql = "UPDATE db_user SET ss_enabled=1 WHERE id IN (%s)" % str(ids)[1:-1]
        cls.query(sql)

    @classmethod
    def get_users_reminder_mail(cls):
        sql = 'SELECT user_name, email, plan_type, plan_end_time FROM db_user WHERE ss_enabled=1 AND plan_type!=free'
        return cls.query(sql)

    @classmethod
    def reset_traffic_zero(cls):
        sql = "UPDATE db_user SET traffic_up=0,traffic_down=0 WHERE plan_type!='free';"
        cls.query(sql)
