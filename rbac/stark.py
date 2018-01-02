#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2018-01-02,16:16"

from stark.service import star
from rbac import models
from django.utils.safestring import mark_safe

class UserConfig(star.StarkConfig):
    list_display = ["id","username","email"]
    edit_link = ["username"]
    show_add_btn = True

class PermissionConfig(star.StarkConfig):

    list_display = ["id","title","url","menu_gp","code","group"]
    show_add_btn = True
    edit_link = ["title"]

class RolesConfig(star.StarkConfig):

    def display_permissions(self,obj=None,is_header = False):
        if is_header:
            return "角色权限"
        lis = []
        permission_list = obj.permissions.all()
        for item in permission_list:
            html = '<span class="span">%s</span>'%item.title
            lis.append(html)

        return mark_safe(''.join(lis))



    list_display = ["id","title",display_permissions]
    show_add_btn = True
    edit_link = [display_permissions]


class MenuConfig(star.StarkConfig):
    list_display = ["id","title"]
    show_add_btn = True

class GroupConfig(star.StarkConfig):
    list_display = ["id","caption","menu"]
    show_add_btn = True
star.site.register(models.User,UserConfig)
star.site.register(models.Permission,PermissionConfig)
star.site.register(models.Roles,RolesConfig)
star.site.register(models.Menu,MenuConfig)
star.site.register(models.Group,GroupConfig)