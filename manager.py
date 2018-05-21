#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Control ss-libev via UDP
import sys
import time

try:
    import config
except ImportError:
    print('[ERROR] Please rename `config_example.py` to `config.py` and setup first!')
    sys.exit(1)

import socket
import logging
import json

# Output log is always at stdout while a log file is optional
logging.basicConfig(format=config.LOG_FORMAT,
                    datefmt=config.LOG_DATE_FORMAT, stream=sys.stdout, level=config.LOG_LEVEL)
if config.LOGFILE_ENABLE:
    logger = logging.getLogger()
    fileLogger = logging.FileHandler(config.LOG_FILE)
    fileLogger.setFormatter(logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT))
    fileLogger.setLevel(config.LOG_LEVEL)
    logger.addHandler(fileLogger)


class Manager:
    BUF_SIZE = 20480  # limit, 20K is enough for 500 users when using get_traffic()
    # currently not need to set buf size smaller and join the data of multi read

    @staticmethod
    def _send_control_msg(message):
        # Consider 4 circumstances:
        # 1. socket.error: sslibev is not running -> connection refused（111）
        # 2. socket.error: sslibev quit during transfer -> batch error will be returned w/o process
        # 3. timeout: no response from sslibev (wrong command or wrong port used by other program)
        # 4. ss is python version instead of libev version
        # Solution:
        # 1,2,3 will all generate socket.error ->
        #       wait x seconds and retry, quit if still fail after retry xx times
        # 4: give the mission to get_traffic() as it will be invoked quite early
        """
        :param message: string
        :return: bytes, b'' means socket error and won't be returned
        """
        retries = config.MESSAGE_MAX_RETRY
        buf = bytes()
        while retries >= 0:
            try:
                cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                cli.settimeout(5)
                cli.connect(('127.0.0.1', config.MANAGER_PORT))
                cli.send(bytes(message, encoding='utf-8'))
                buf = cli.recv(Manager.BUF_SIZE)
                cli.close()
            except socket.error as e:
                retries -= 1
                if retries >= 0:
                    logging.warning('"%s" - retry(x%d) %d seconds later'
                                    % (e, config.MESSAGE_MAX_RETRY-retries, config.MESSAGE_RETRY_INTERVAL))
                    time.sleep(config.MESSAGE_RETRY_INTERVAL)
                else:
                    logging.critical('Socket retry times reached limit, now quit')
                    sys.exit(1)
            else:
                break
        return buf

    @staticmethod
    def add_port(port, password):
        message = 'add: {"server_port": %d, "password":"%s"}' % (port, password)
        return Manager._send_control_msg(message)

    @staticmethod
    def remove_port(port):
        message = 'remove: {"server_port": %d}' % port
        return Manager._send_control_msg(message)

    @staticmethod
    def update_port(port, password):
        Manager.remove_port(port)
        return Manager.add_port(port, password)

    @staticmethod
    def get_traffic():
        """:return dict, like {123:0, 124:162238} """
        buf = Manager._send_control_msg('ping')
        # buf is like: b'stat: {"8001":0,"8002":0}' or b'' (error happened, should not be returned)
        result = {}
        if len(buf) > 6:
            dict_temp = json.loads(buf[6:])
            for s in dict_temp:
                result.update({int(s): dict_temp[s]})
        elif buf == b'pong':
            logging.critical('Client is ss-python instead of ss-libev, not supported.')
            sys.exit(1)
        return result

    @staticmethod
    def get_working_ports():
        """ :return list, might be [] but not None """
        return list(Manager.get_traffic())

    # @staticmethod
    # def get_ports_details():
    #     """no need and not recommended
    #     :return bytes"""
    #     return Manager._send_control_msg('list')
