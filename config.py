#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Store configurations

import logging

# MANAGER_PORT = 6022
MANAGER_PORT = 6001

DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_NAME = 'ssman'

# Time interval between 2 pulls from the database or API (in seconds)
DB_PULL_INTERVAL = 30
# log traffic histories in database
DB_LOG_TRAFFIC = True
DB_LOG_TRAFFIC_INTERVAL = 300


# Max retries before ssman exit if can't connect to manager port
MESSAGE_MAX_RETRY = 30
MESSAGE_RETRY_INTERVAL = 10


# Logging settings
LOG_LEVEL = logging.INFO  # can be logging.NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
# LOG_FORMAT = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'  # for debugging
LOG_DATE_FORMAT = '%b %d %H:%M:%S'
# Log is always at stdout, the log file is optional:
LOGFILE_ENABLE = False  # set to False if you use supervisor to handle the log
LOG_FILE = '/tmp/shadowsocks.log'


# Email settings
# There is no switch for reminder mail, just don't run it if you don't need it
MAIL_HOST = 'smtp.xxx.com'
MAIL_FROM = 'your name'
MAIL_PORT = 465
MAIL_USER = 'youremail@xxx.com'
MAIL_PASSWORD = 'your_email_password'
