#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-28,23:02"
import importlib

from django.conf import settings
from crmpro.utils.message.email import Email

def send_message(subject,body,to,name):
    '''
    短信，微信，短信
    :param subject:
    :param body:
    :param to:
    :param name:
    :return:
    '''

    for cls_path in settings.MESSAGE_CLASSES:

        module_path,class_name = cls_path.rsplit(".",maxsplit = 1)

        m = importlib.import_module(module_path)


        obj = getattr(m,class_name)()#实例化

        obj.send(subject,body,to,name)