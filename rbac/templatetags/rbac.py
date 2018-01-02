#!/usr/bin/env python
#-*- coding:utf-8 -*-
#Author:沈中秋
#date:"2017-12-02,20:14"

import re

from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag("base_sidbar.html")
# def menu_html(request):
#     menu_list = request.session[settings.PERMISSION_MENU_KEY]  # 从session 中取出菜单列表
#     current_url = request.path_info  # 获取当前的路径
#     result = {}  # 定义一个空字典，准备构造数据结构
#     for item in menu_list:  # 循环菜单列表
#         url = item["url"]  # 取出列表中的url
#         regex = '^{0}'.format(url)  # 格式化url,加上正则
#         active = False
#         if re.match(regex, current_url):  # 利用re模块中的match将当前url和从session中取出的url匹配
#             active = True  # 匹配成功，状态改为True
#
#         menu_id = item["menu_id"]  # 获取菜单id
#         if menu_id in result:  # 如果result中有menu_id 的情况，表明这不是第一次循环
#             result[menu_id]["children"].append({"title": item["title"], "url": url, "active": active})
#             # 如果children的active是True,那么将菜单的active也改为True
#             # 这个怎么理解呢，如果第一次循环的时候没有匹配上的话，那么菜单的active是False,但是如果第二次循环的时候匹配上了，这个时候就需要将菜单的active该为True
#             if active:
#                 result[menu_id]["active"] = True
#         else:  # 这一步是最重要的，构造数据结构
#             result[menu_id] = {
#                 "menu_id": menu_id,
#                 "menu_title": item["menu_title"],
#                 "active": active,
#                 "children": [
#                     {"title": item["title"], "url": url, "active": active}
#                 ]
#
#             }
#     return {"menu_dict":result}

def menu_html(request):
    '''
    去session中获取菜单相关信息，匹配当前url,生成菜单
    :param request:
    :return:
    '''
    menu_list = request.session[settings.PERMISSION_MENU_KEY]
    current_url = request.path_info

    menu_dict = {}

    for item in menu_list:
        if not item["menu_gp_id"]:  #说明是菜单
            menu_dict[item["id"]] = item # 以id 为健，item本身为value构建字典

    for item in menu_list:
        regex = "^{0}$".format(item["url"])
        if re.match(regex,current_url):
            menu_gp_id = item["menu_gp_id"]
            if menu_gp_id:
                menu_dict[menu_gp_id]["active"] = True #如果有id 表名不是菜单，找到这个menu_gp_id 对应的value给它加上active = True
            else:
                #如果没有id,表名本身就是菜单(注意，这里是通过item["id"]来找到这个健的），直接加active = True
                menu_dict[item["id"]]["active"] = True

    result = {}
    for item in menu_dict.values():
        active = item.get("active")
        menu_id = item["menu_id"]
        if menu_id in result:
            result[menu_id]["children"].append( {"title":item["title"],"url":item["url"],"active":active})
        else:
            result[menu_id] = {
                "menu_id":item["menu_id"],
                "menu_title":item["menu_title"],
                "active":active,
                "children":[
                    {"title":item["title"],"url":item["url"],"active":active}
                ]

            }
    return {"menu_dict":result}

'''
menu_list = [
    {'id': 1, 'title': '用户列表', 'url': '/userinfo/', 'menu_gp_id': None, 'menu_id': 1, 'menu_title': '菜单管理'},
    {'id': 2, 'title': '添加用户', 'url': '/userinfo/add/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'},
    {'id': 3, 'title': '删除用户', 'url': '/userinfo/del/(\\d+)/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'},
    {'id': 4, 'title': '修改用户', 'url': '/userinfo/edit/(\\d+)/', 'menu_gp_id': 1, 'menu_id': 1, 'menu_title': '菜单管理'},

    {'id': 5, 'title': '订单列表', 'url': '/order/', 'menu_gp_id': None, 'menu_id': 2, 'menu_title': '菜单2'},
    {'id': 6, 'title': '添加订单', 'url': '/order/add/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'},
    {'id': 7, 'title': '删除订单', 'url': '/order/del/(\\d+)/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'},
    {'id': 8, 'title': '修改订单', 'url': '/order/edit/(\\d+)/', 'menu_gp_id': 5, 'menu_id': 2, 'menu_title': '菜单2'}
]

menu_dict = {
    1: {'id': 1, 'title': '用户列表', 'url': '/userinfo/', 'menu_gp_id': None, 'menu_id': 1, 'menu_title': '用户管理'},
    5: {'id': 5, 'title': '订单列表', 'url': '/order/', 'menu_gp_id': None, 'menu_id': 2, 'menu_title': '订单管理'},
}
'''



