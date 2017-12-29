#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-28,23:04"


class BaseMessage(object):
    def send(self,subject,body,to,name):
        raise NotImplemented("未实现send方法")
