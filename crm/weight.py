#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-28,19:49"
from crm import models

class AutoSale(object):
    users= None
    iter_users = None
    reset_status = None
    rollback_list = []

    @classmethod
    def fetch_user(cls):
        '''
        获取客户id根据转化人数依次放入列表中
        :return:
        '''
        sales = models.SaleRank.objects.all().order_by("-weight")
        sale_id_list = []
        count= 0
        while True:
            flag = False
            for row in sales:
                if count<row.num:
                    sale_id_list.append(row.user_id)
                    flag = True
            count += 1
            if not flag:
                break
        cls.users = sale_id_list

    @classmethod
    def get_sale_id(cls):
        if cls.rollback_list:
            return cls.rollback_list.pop()

        if not cls.users:
            cls.fetch_user()
        if not cls.users:
            return None

        if not cls.iter_users:
            cls.iter_users = iter(cls.users)
        try:
            user_id = next(cls.iter_users)
        except StopIteration as e:
            if cls.reset_status:
                cls.fetch_user()
                cls.reset_status = False
            cls.iter_users = iter(cls.users)
            user_id = cls.get_sale_id()
        return user_id

    @classmethod
    def reset(cls):
        cls.reset_status = True

    @classmethod
    def rollback(cls,nid):
        cls.rollback_list.insert(0,nid)#多线程会出现多个值，所以用insert


