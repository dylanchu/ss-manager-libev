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

from database import Database as db
import logging

# Log is always at stdout while a log file is optional
logging.basicConfig(format=config.LOG_FORMAT,
                    datefmt=config.LOG_DATE_FORMAT, stream=sys.stdout, level=config.LOG_LEVEL)
if config.LOGFILE_ENABLE:
    logger = logging.getLogger()
    fileLogger = logging.FileHandler(config.LOG_FILE)
    fileLogger.setFormatter(logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT))
    fileLogger.setLevel(config.LOG_LEVEL)
    logger.addHandler(fileLogger)


def check_users():
    all_users = db.get_all_users()
    if not all_users:
        return
    time_now = datetime.datetime.now()
    users_to_disable = []
    users_to_enable = []
    reasons = {-1: 'User Level < 0', -2: 'Bandwidth Exceeded', -3: 'Expired'}
    for u in all_users:
        # 0     1        2        3       4           5             6             7
        # id,ss_port,ss_enabled,level,traffic_up,traffic_down,traffic_enabled,plan_end_time
        qualified = 1
        if u[3] < 0:
            qualified = -1
        elif u[4] + u[5] > u[6]:
            qualified = -2
        elif u[7] < time_now:
            qualified = -3
        if u[2] and qualified < 0:
            users_to_disable.append(u[0])
            logging.info('U[%d] P[%d] will be disabled: %s' % (u[0], u[1], reasons[qualified]))
        elif not u[2] and qualified == 1:
            users_to_enable.append(u[0])
            logging.info('U[%d] P[%d] will be enabled' % (u[0], u[1]))
    db.disable_user(users_to_disable)
    db.enable_user(users_to_enable)


if __name__ == '__main__':
    check_users()
