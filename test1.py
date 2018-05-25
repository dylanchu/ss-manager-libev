#!/usr/bin/python3
# -*- coding: utf-8 -*-

from manager import Manager
from database import Database as db


def remove_batch(a, b):
    Manager.remove_ports(range(a, b + 1))


def add_batch(a, b):
    aim_accounts = {1080: 'adsfadfs'}
    # aim_accounts = {}
    for i in range(a, b+1):
        aim_accounts.update({i: 'asdfasdfasdfasdfasdfasdf'})
    return Manager.add_ports(aim_accounts)


def update_batch(a, b):
    aim_accounts = {1080: 'adsfadfs'}
    for i in range(a, b+1):
        aim_accounts.update({i: 'asdfasdf'})
    return Manager.update_ports(aim_accounts)


def update_used_traffic():
    traffics_to_add = {12009: 1000, 12011: 1000}
    # for i in range(5):
    #     traffics_to_add.update({i+17800: 154782362980})
    # print(traffics_to_add)
    db.push_used_traffic(traffics_to_add)


def log_traffic():
    traffics_to_log = {12009: 1000, 12011: 1000}
    db.log_traffic_history(traffics_to_log)
