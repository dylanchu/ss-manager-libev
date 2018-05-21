#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Reset used traffic of none free accounts to 0

from database import Database as db

if __name__ == '__main__':
    db.reset_traffic_zero()
