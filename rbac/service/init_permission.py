#!/usr/bin/env python
#-*- coding:utf-8 -*-
#Author:沈中秋
#date:"2017-12-02,0:26"

from django.conf import settings



def init_permission(user,request):
    '''
    获取权限信息列表，放入session中
    :param user:
    :param request:
    :return:
    '''

    permission_list = user.roles.values(
        "permissions__id",
        "permissions__title",#权限名
        "permissions__url",#url
        "permissions__code",#url对应的代码
        # "permissions__is_menu",#是否是菜单
        "permissions__group_id",#组id
        "permissions__menu_gp_id",#组内菜单id,为空表示是菜单
        "permissions__group__menu_id", #菜单id
        "permissions__group__menu__title",#菜单名


    ).distinct() #获取权限信息列表，并去重


    sub_permission = []
    for item in permission_list:
        tpl = {
            "id":item["permissions__id"],
            "title":item["permissions__title"],
            "url":item["permissions__url"],
            "menu_gp_id":item["permissions__menu_gp_id"],
            "menu_id":item["permissions__group__menu_id"],
            "menu_title":item["permissions__group__menu__title"]
        }
        sub_permission.append(tpl)
    request.session[settings.PERMISSION_MENU_KEY] = sub_permission



    #生成这样的数据结构
    '''
    data = {
			1: {
				'codes': ['list','add','edit','del'],
				'urls':[
					/userinfo/,
					/userinfo/add/,
					/userinfo/edit/(\d+)/,
					/userinfo/del/(\d+)/,
				]
			},
			2: {
				'codes': ['list','add','edit','del'],
				'urls':[
					/userinfo/,
					/userinfo/add/,
					/userinfo/edit/(\d+)/,
					/userinfo/del/(\d+)/,
				]
			},

		}
    '''
    result = {}
    for item in permission_list:
        group_id = item["permissions__group_id"]
        code = item["permissions__code"]
        url = item["permissions__url"]

        if group_id in result:
            result[group_id]["codes"].append(code)
            result[group_id]["urls"].append(url)
        else:
            result[group_id] = {
                "codes":[code,],
                "urls":[url,]
            }

    request.session[settings.PERMISSION_URL_DICT_KEY] = result
