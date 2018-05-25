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


class Socket(object):
    BUF_SIZE = 20480  # limit, 20K is enough for 500 users when using get_traffics()

    def __enter__(self):
        self.cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cli.settimeout(5)
        self.cli.connect(('127.0.0.1', config.MANAGER_PORT))
        return self

    # currently no need to set buf size smaller and join the data of multi read
    def send(self, message):
        # Consider 4 circumstances:
        # 1. socket.error: sslibev is not running -> connection refused（111）
        # 2. socket.error: sslibev quit during transfer -> batch error will be returned w/o process
        # 3. timeout: no response from sslibev (wrong command or wrong port used by other program)
        # 4. ss is python version instead of libev version
        # Solution:
        # 1,2,3 will all generate socket.error ->
        #       wait x seconds and retry, quit if still fail after retry xx times
        # 4: give the mission to get_traffics() as it will be invoked quite early
        """
        :param message: string
        :return: bytes, b'' means socket error and won't be returned
        """
        retries = config.MESSAGE_MAX_RETRY
        buf = bytes()
        while retries >= 0:
            try:
                self.cli.send(bytes(message, encoding='utf-8'))
                buf = self.cli.recv(self.BUF_SIZE)
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

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cli.close()
#


class Manager(object):
    @classmethod
    def get_traffics(cls):
        """:return dict, like {123:0, 124:162238} """
        with Socket() as sk:
            buf = sk.send('ping')
            # buf may be like: b'stat: {"8001":0,"8002":0}' or b'' or b'pong'(ss-python)
            result = {}
            if len(buf) > 6:
                dict_temp = json.loads(buf[6:])
                for s in dict_temp:
                    result.update({int(s): dict_temp[s]})
            elif buf == b'pong':
                logging.critical('Client is ss-python instead of ss-libev, not supported.')
                sys.exit(1)
            return result

    @classmethod
    def get_working_ports(cls):
        """ :return list, might be [] but not None """
        return list(cls.get_traffics())

    # @classmethod
    # def get_ports_details(cls):
    #     """no need and not recommended
    #     :return bytes"""
    #     with Socket() as sk:
    #         return sk.send('list')

    @classmethod
    def add_ports(cls, aim_ports):
        """aim_ports: dict, like {8001:'aaaa', 8002:'bbbb'}
        return: None or list, of failed ports like [8001, 8002]
        """
        if not aim_ports:
            return
        ports_retry = {}
        with Socket() as sk:
            for p in aim_ports:
                result = sk.send('add: {"server_port": %d, "password":"%s"}' % (p, aim_ports[p]))
                time.sleep(0.01)
                # print('%d %s' % (p, result))
                if result == b'ok':
                    logging.debug('Added:  P[%d]' % p)
                else:
                    ports_retry.update({p: aim_ports[p]})
            for i in (1, 2, 3):
                if ports_retry:
                    ports_temp = ports_retry.copy()    # need .copy()
                    logging.warning('Retry %d: Add Another %d Ports' % (i, len(ports_retry)))
                    for p in ports_temp:
                        result = sk.send('add: {"server_port": %d, "password":"%s"}' % (p, ports_temp[p]))
                        if result == b'ok':
                            logging.debug('Added:  P[%d]' % p)
                            del ports_retry[p]
                        elif i == 3:
                            logging.error('Add:   P[%d] FAILED -> "%s"' % (p, str(result, encoding='utf-8')))
                else:
                    break
            else:
                if ports_retry:
                    logging.error('After 3 Retries: Still %d ports failed to be added' % len(ports_retry))
                    logging.error('Failed ports are: %s' % list(ports_retry))
                    return list(ports_retry)

    @classmethod
    def remove_ports(cls, aim_ports):
        """aim_ports: list, like [8001, 8002]
        return: None or list, like [8001, 8002]
        """
        if not aim_ports:
            return
        ports_retry = []
        with Socket() as sk:
            for p in aim_ports:
                result = sk.send('remove: {"server_port": %d}' % p)
                # print('%d %s' % (p, result))
                if result == b'ok':
                    logging.debug('Removed:  P[%d]' % p)
                else:
                    ports_retry.append(p)
            if ports_retry:
                # retry: only retry one time
                ports_failed = []
                logging.warning('Retry: Remove Another %d Ports' % len(ports_retry))
                for p in ports_retry:
                    result = sk.send('remove: {"server_port": %d}' % p)
                    if result == b'ok':
                        logging.debug('Removed:  P[%d]' % p)
                    else:
                        ports_failed.append(p)
                        logging.error('Remove:   P[%d] FAILED -> "%s"' % (p, str(result, encoding='utf-8')))
                else:
                    if ports_failed:
                        logging.error('After Retry: Still %d ports failed to be removed' % len(ports_failed))
                        logging.error('Failed ports are: %s' % ports_failed)
                        return ports_failed

    @classmethod
    def update_ports(cls, aim_ports):
        """aim_ports: dict, like {8001:'aaaa', 8002:'bbbb'}
        return: None or list, of failed ports like [8001, 8002]
        """
        cls.remove_ports(list(aim_ports))
        return cls.add_ports(aim_ports)
