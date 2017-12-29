#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-27,17:23"
from django.conf import settings
from django.shortcuts import redirect

class MiddlewareMixin(object):  #写中间件必须继承这个类
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

class LoginMiddleware(MiddlewareMixin):
    '''
    登录验证
    '''
    def process_request(self,request):

        if request.path_info == "/login/":
            return None
        elif request.session.get(settings.LOGIN_INFO):
            return None
        else:
            return redirect('/login/')



