#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2019/6/8

import config
from datetime import datetime
from sqlalchemy import Column, String, Integer, SmallInteger, SMALLINT, create_engine, VARCHAR, BigInteger, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    note = Column(VARCHAR(128), nullable=True, default=None)
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(32), nullable=False)
    level = Column(SmallInteger, nullable=False, default=0)
    email = Column(VARCHAR(48), nullable=False, unique=True)
    password = Column(VARCHAR(48), nullable=False, default='888888')
    ss_port = Column(Integer, nullable=False, unique=True)
    ss_pwd = Column(VARCHAR(16), nullable=False)
    ss_enabled = Column(SMALLINT, nullable=False, default=1)
    ss_method = Column(String(32), nullable=False, default='aes-128-cfb')
    traffic_up = Column(BigInteger, nullable=False, default=0)
    traffic_down = Column(BigInteger, nullable=False, default=0)
    traffic_quota = Column(BigInteger, nullable=False, default=0)
    last_use_time = Column(DateTime, default=DateTime('2000-01-01 08:00:00'))
    plan_type = Column(String(32), nullable=False, default='free')
    plan_end_time = Column(DateTime, default=DateTime('2000-01-01 08:00:00'))
    total_paid = Column(Integer, default=0)
    reg_time = Column(DateTime, default=lambda x: datetime.utcnow())
    reg_ip = Column(String(39), default='127.0.0.1')


if __name__ == '__main__':
    # 初始化数据库连接:
    engine = create_engine('mysql+cymysql://%s:%s@%s:%s/%s' % (config.DB_USER, config.DB_PASSWORD, config.DB_HOST,
                                                               config.DB_PORT, config.DB_NAME))
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)

    # 创建session对象:
    session = DBSession()
    # 创建新User对象:
    new_user = User(name='Bob')
    # 添加到session:
    session.add(new_user)
    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()
