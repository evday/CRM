#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-21,22:53"

from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.shortcuts import redirect,HttpResponse
from django.conf.urls import url

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

class CustomerConfig(star.StarkConfig):
    show_add_btn = True
    edit_link = ["qq",]
    def display_gender(self,obj = None,is_header = False):
        if is_header:
            return "性别"
        return obj.get_gender_display()
    def display_course(self,obj = None,is_header = False):
        if is_header:
            return "咨询课程"
        course_list = obj.course.all()
        html = []
        #构造标签
        for item in course_list:
            temp = "<a style='display:inline-block;padding:3px 5px;border:1px solid blue;margin:2px;' href='/stark/crm/customer/%s/%s/dc/'>%s<span class='glyphicon glyphicon-remove'></span></a>"%(obj.pk,item.pk,item.name)
            html.append(temp)
        return mark_safe("".join(html))

    def display_status(self,obj = None,is_header = False):
        if is_header:
            return "状态"
        return obj.get_status_display()

    def record(self,obj = None,is_header = False):
        if is_header:
            return '跟进记录'
        return mark_safe("<a href='/stark/crm/consultrecord/?customer = %s'>查看跟进记录</a>"%(obj.pk))


    list_display = ["qq","name",display_gender,display_course,display_status,record]

    def delete_course(self,request,customer_id,course_id):
        '''
        删除当前客户感兴趣的课程
        :param request:
        :param customer_id:
        :param course_id:
        :return:
        '''
        customer_obj = self.model_class.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        return redirect(self.get_changelist_url())

    def extra_url(self):
        '''
        扩展除增删改查之外的url
        :return:
        '''
        app_model_name = (self.model_class._meta.app_label,self.model_class._meta.model_name,)
        patterns = [
            url(r'^(\d+)/(\d+)/dc/$',self.wrapper(self.delete_course),name="%s_%s_dc"%app_model_name)
        ]
        return patterns

star.site.register(models.Customer,CustomerConfig)


class ConsultRecordConfig(star.StarkConfig):
    list_display = ["customer","consultant","date"]
    show_add_btn = True
    comb_filters = [
        star.FilterOption("customer")
    ]
    def changelist_view(self,request,*args,**kwargs):
        customer = request.GET.get("customer")
        # session 中获取当前用户ID
        current_login_user_id = 6
        ct = models.Customer.objects.filter(consultant=current_login_user_id,id=customer).count()
        if not ct:
            return HttpResponse("别抢客户呀...")
        return super(ConsultRecordConfig,self).changelist_view(request,*args,**kwargs)
star.site.register(models.ConsultRecord,ConsultRecordConfig)