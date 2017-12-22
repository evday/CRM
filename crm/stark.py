#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-21,22:53"

from django.forms import ModelForm

from stark.service import star
from crm import models


class DepartmentConfigForm(ModelForm):
    class Meta:
        model = models.Department
        fields = "__all__"
        error_messages = {
            "title": {"required": "部门名称不能为空"},
            "code": {
                "required": "部门编号不能为空",
            }
        }

class DepartmentConfig(star.StarkConfig):

    list_display = ["title","code"]

    def get_list_display(self):
        result = []
        result.extend(self.list_display)
        result.append(star.StarkConfig.edit)
        result.append(star.StarkConfig.delete)
        result.insert(0,star.StarkConfig.checkbox)
        return result
    show_add_btn = True
    edit_link = ["title",]
    model_form_class = DepartmentConfigForm
star.site.register(models.Department,DepartmentConfig)


class UserInfoConfigForm(ModelForm):
    class Meta:
        model = models.UserInfo
        fields = "__all__"
        error_messages = {
            "name": {"required": "员工不能为空"},
            "password": {"required": "密码不能为空"},
            "email": {"required": "邮箱不能为空"},
            "depart": {"required": "部门编号不能为空"},
            "username": {
                "required": "用户名不能为空",
            }
        }

class UserInfoConfig(star.StarkConfig):
    list_display = ["name","username","email","depart"]

    def multi_del(self,request):

        print(request.POST)
        pk_list = request.POST.getlist("pk") #这个pk是我们在checkbook方法设置的

        self.model_class.objects.filter(id__in = pk_list).delete()
    multi_del.short_desc = "批量删除"

    actions = [multi_del,]
    comb_filters = [
        star.FilterOption("depart",text_func_name = lambda x:str(x),val_func_name = lambda x:str(x.code))
    ]
    show_add_btn = True
    edit_link = ["name","username"]
    show_search_form = True
    show_actions = True
    search_fields = ["name__contains","email__contains"]
    model_form_class = UserInfoConfigForm
star.site.register(models.UserInfo,UserInfoConfig)


class CourseConfigForm(ModelForm):
    class Meta:
        model = models.Course
        fields = "__all__"
        error_messages = {
            "name": {"required": "课程名称不能为空"},
        }

class CourseConfig(star.StarkConfig):
    list_display = ["name",]
    edit_link = ["name",]
    show_add_btn = True
    model_form_class = CourseConfigForm
star.site.register(models.Course,CourseConfig)



class SchoolConfigForm(ModelForm):
    class Meta:
        model = models.School
        fields = "__all__"
        error_messages = {
            "title": {"required": "校区名称不能为空"},
        }

class SchoolConfig(star.StarkConfig):
    list_display = ["title",]
    edit_link = ["title",]
    show_add_btn = True
    model_form_class = SchoolConfigForm
star.site.register(models.School,SchoolConfig)

class ClassListConfig(star.StarkConfig):
    def course_semester(self,obj = None,is_header = False):
        if is_header:
            return "班级"
        return "%s(%s期)"%(obj.course.name,obj.semester)

    def num(self,obj = None,is_header = False):
        if is_header:
            return "人数"
        return "%s人" % obj.student_set.all().count()

    list_display = ["school",course_semester,num,"start_date"]
    show_add_btn = True
    edit_link = [course_semester,]

star.site.register(models.ClassList,ClassListConfig)
