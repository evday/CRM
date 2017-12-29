#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-28,19:49"
import redis

from django.conf import settings

from crm import models


POOL = redis.ConnectionPool(host = "192.168.20.150",port=6379)
CONN = redis.Redis(connection_pool = POOL)

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
        print(sale_id_list,'------------------')
        if sale_id_list:
            CONN.rpush(settings.SALE_ID_LIST,*sale_id_list)
            CONN.rpush(settings.SALE_ID_LIST_ORIGIN,*sale_id_list)
            return True
        return False

    @classmethod
    def get_sale_id(cls):
        #查看原数据是否存在
        sale_id_origin_count = CONN.llen(settings.SALE_ID_LIST_ORIGIN)
        if not sale_id_origin_count:
            # 如果不存在就去数据库中获取，并赋值给原数据和pop数据
            status = cls.fetch_user()
            if not status:
                return None #数据库中未获取到sale_id

        user_id = CONN.lpop(settings.SALE_ID_LIST)
        if user_id:
            return user_id

        reset = CONN.get(settings.SALE_ID_RESET)

        #数据库跟新需重置原数据
        if reset:
            CONN.delete(settings.SALE_ID_LIST_ORIGIN)
            status = cls.fetch_user()
            if not status:
                return None
            CONN.delete(settings.SALE_ID_RESET)
            return CONN.lpop(settings.SALE_ID_LIST)
        else:
            ct = CONN.llen(settings.SALE_ID_LIST_ORIGIN)
            for i in range(ct):
                v = CONN.lindex(settings.SALE_ID_LIST_ORIGIN,i)#根据索引取值
                CONN.rpush(settings.SALE_ID_LIST,v)
            return CONN.lpop(settings.SALE_ID_LIST)

    @classmethod
    def reset(cls):
        CONN.set(settings.SALE_ID_RESET,1)

    @classmethod
    def rollback(cls,nid):
        CONN.lpush(settings.SALE_ID_LIST,nid) #rollback 和 sale_id_list 公用一个列表


