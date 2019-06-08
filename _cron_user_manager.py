#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Check traffic and expiring time. Only Database Server need this. Using it via CRON.
import datetime
import sys

try:
    import config
except ImportError:
    print('[ERROR] Please rename `config_example.py` to `config.py` first!')
    sys.exit('config not found')

from config import logger
from database import Database as db


def check_users():
    all_users = db.get_all_users()
    if not all_users:
        return
    time_now = datetime.datetime.now()
    users_to_disable = []
    users_to_enable = []
    reasons = {-1: 'User Level < 0', -2: 'Bandwidth Exceeded', -3: 'Expired'}
    for uid, email, ss_port, ss_enabled, level, traffic_up, traffic_down, traffic_quota, plan_end_time in all_users:
        # 0     1        2        3       4           5             6             7
        # id,ss_port,ss_enabled,level,traffic_up,traffic_down,traffic_quota,plan_end_time
        status = 1  # normal
        if level < 0:
            status = -1
        elif traffic_up + traffic_down >= traffic_quota:
            status = -2
        elif plan_end_time < time_now:
            status = -3
        if ss_enabled and status < 0:
            users_to_disable.append(uid)
            logger.info('U[%d] P[%d] will be disabled: %s. Email[%s]' % (uid, ss_port, reasons[status], email))
        elif not ss_enabled and status == 1:
            users_to_enable.append(uid)
            logger.info('U[%d] P[%d] will be enabled. Email[%s]' % (uid, ss_port, email))
    db.disable_user(users_to_disable)
    db.enable_user(users_to_enable)


if __name__ == '__main__':
    check_users()
