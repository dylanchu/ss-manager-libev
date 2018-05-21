#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# User management and traffic log control
import gc
import sys

try:
    import config
except ImportError:
    print('[ERROR] Please rename `config_example.py` to `config.py` first!')
    sys.exit('config not found')

from manager import Manager
from database import Database as db
import logging
import time

# Output log is always at stdout while a log file is optional
logging.basicConfig(format=config.LOG_FORMAT,
                    datefmt=config.LOG_DATE_FORMAT, stream=sys.stdout, level=config.LOG_LEVEL)
if config.LOGFILE_ENABLE:
    logger = logging.getLogger()
    fileLogger = logging.FileHandler(config.LOG_FILE)
    fileLogger.setFormatter(logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT))
    fileLogger.setLevel(config.LOG_LEVEL)
    logger.addHandler(fileLogger)


class SSManager:
    def __init__(self):
        """
        When start, a bad situation is:
        ss was already serving some ports, then the password in database changed, and ssman
        started after that. Then there will be a password update problem.
        A solution is: remove all and add enabled, store _ports_working for passwords update
        """
        logging.warning('Start Ssman for ss-libev, now initializing...')
        self._ports_working = {}
        self._traffics_lasttime = {}
        self._traffics_to_log = {}
        self._traffic_sync_n = 0
        # fetch serving ports before ssman start
        ports_failed = self.remove_ports(Manager.get_working_ports())
        if ports_failed is not None:
            for p in ports_failed:
                self._ports_working.update({p: None})

        ports_enabled = db.get_enabled_ports()
        ports_failed = self.add_ports(ports_enabled)

        # and store the passwords for later sync passwords
        self._ports_working.update(ports_enabled)
        if ports_failed is not None:
            for p in ports_failed:
                if p in self._ports_working:
                    del self._ports_working[p]
        logging.info('Initial working ports: %s' % list(self._ports_working))
        logging.warning('Initialization done.')

    @classmethod
    def add_ports(cls, aim_ports):
        """aim_ports: dict, like {8001:'aaaa', 8002:'bbbb'}
        return: None or list, of failed ports like [8001, 8002]
        """
        if not aim_ports:
            return
        ports_retry = {}
        for p in aim_ports:
            result = Manager.add_port(p, aim_ports[p])
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
                    result = Manager.add_port(p, ports_temp[p])
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
        for p in aim_ports:
            result = Manager.remove_port(p)
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
                result = Manager.remove_port(p)
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

    def sync_ports(self):
        """sslibev should only be managed by this single thread, then right ports
        and passwords can be ensured. If you use other tools like UDP debugger to
        change the port number, ssman will reset it according to database. But if
        you kill the process manually, if will not be corrected as sslibev cannot
        detect that. Direct manually password change wont be corrected.
        """
        logging.debug('sync ports...')
        ports_to_add = dict()
        ports_to_update = dict()
        ports_to_remove = list()
        # get real working ports
        old_ports_list = Manager.get_working_ports()
        temp_dict = self._ports_working.copy()
        for p in temp_dict:
            if p not in old_ports_list:
                del self._ports_working[p]
        for p in old_ports_list:
            if p not in self._ports_working:
                self._ports_working.update({p: None})

        ports_enabled = db.get_enabled_ports()
        for p in ports_enabled:
            if p in self._ports_working:
                if self._ports_working[p] != ports_enabled[p]:
                    ports_to_update.update({p: ports_enabled[p]})
            else:
                ports_to_add.update({p: ports_enabled[p]})
        for p in self._ports_working:
            if p not in ports_enabled:
                ports_to_remove.append(p)
        if ports_to_remove:
            logging.info('Sync: Will Remove P%s' % ports_to_remove)
            ports_failed = self.remove_ports(ports_to_remove)
            if ports_failed is None:    # better than try
                for p in ports_to_remove:
                    del self._ports_working[p]
            else:
                for p in ports_to_remove:
                    if p not in ports_failed:
                        del self._ports_working[p]
        if ports_to_update:
            logging.info('Sync: Will Update P%s' % list(ports_to_update))
            ports_failed = self.update_ports(ports_to_update)    # subset of ports_to_update
            # then handle _ports_working:
            self._ports_working.update(ports_to_update)
            if ports_failed is not None:
                for p in ports_failed:
                    del self._ports_working[p]
        if ports_to_add:
            logging.info('Sync: Will Add    P%s' % list(ports_to_add))
            ports_failed = self.add_ports(ports_to_add)    # subset of ports_to_add
            # then handle _ports_working:
            self._ports_working.update(ports_to_add)
            if ports_failed is not None:
                for p in ports_failed:
                    del self._ports_working[p]
        del ports_to_add, ports_to_remove, ports_to_update, ports_enabled, old_ports_list

    def sync_traffics(self):
        logging.debug('sync traffics...')
        traffics_periodic = {}
        traffics_to_add = {}
        traffics_read = Manager.get_traffic()
        for p in traffics_read:
            if p in self._traffics_lasttime:
                traffics_periodic.update({p: traffics_read[p] - self._traffics_lasttime[p]})
            else:
                traffics_periodic.update({p: traffics_read[p]})
        for p in traffics_periodic:
            if traffics_periodic[p] != 0:
                traffics_to_add.update({p: traffics_periodic[p]})

        db.push_used_traffic(traffics_to_add)

        self._traffics_lasttime = traffics_read    # .copy()?

        if config.DB_LOG_TRAFFIC:
            for p in traffics_periodic:
                if traffics_periodic[p] != 0:
                    if p in self._traffics_to_log:
                        self._traffics_to_log.update({p: self._traffics_to_log[p] + traffics_periodic[p]})
                    else:
                        self._traffics_to_log.update({p: traffics_periodic[p]})
            # if time to log traffic:
            self._traffic_sync_n += 1
            if self._traffic_sync_n * config.DB_PULL_INTERVAL >= config.DB_LOG_TRAFFIC_INTERVAL:
                db.log_traffic_history(self._traffics_to_log)
                self._traffics_to_log.clear()
                self._traffic_sync_n = 0
        del traffics_periodic, traffics_read, traffics_to_add


if __name__ == '__main__':
    ssman = SSManager()
    while True:
        ssman.sync_ports()
        gc.collect()
        time.sleep(config.DB_PULL_INTERVAL)
        ssman.sync_traffics()
