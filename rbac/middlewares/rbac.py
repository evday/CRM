#!/usr/bin/env python
#-*- coding:utf-8 -*-
#Author:沈中秋
#date:"2017-12-02,1:34"
import re

from django.conf import settings
from django.shortcuts import redirect,HttpResponse



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


class RbacMiddleware(MiddlewareMixin):

    def process_request(self,request):#中间件有两个方法，一个process_request 一个response_request
        '''
        1 获取当前请求的url
        current_url = request.path_info

        2 获取session中保存的当前用户的权限
        request.session.get("permission_url_list")
        :param request:
        :return:
        '''
        current_url = request.path_info


        #当前请求的url不需要执行验证的（白名单），在settings中设置
        for url in settings.VALID_URL:
            regex = "^{0}$".format(url) #加上正则
            if re.match(regex,current_url): # 将白名单的url和当前用户请求的url匹配
                return None#return None 表示继续往内层中间件走

        permission_dict = request.session.get(settings.PERMISSION_URL_DICT_KEY)#获取放置在session中的当前用户的权限

        if not permission_dict:#如果session中没有值，说明用户还未登陆，跳转到登录页面
            return redirect("/login/")



        flag = False#设置 标志位
        for group_id,code_url in permission_dict.items():
            for db_url in code_url["urls"]:
                regex = "^{0}$".format(db_url)  # 加上正则
                if re.match(regex, current_url):
                    request.permission_code_list = code_url["codes"] # 主动给request中添加一个permission_code_list
                    flag = True
                    break
            if flag:
                break
        if not flag:
            return HttpResponse("无权访问")
            ################写完中间件一定要在settings中添加进去 'rbac.middlewares.rbac.RbacMiddleware'