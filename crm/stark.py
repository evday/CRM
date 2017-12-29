#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-21,22:53"

from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.shortcuts import redirect,HttpResponse
from django.conf.urls import url
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings

from stark.service import star
from crm import models
from crm.configs.student import StudentConfig
from crm.configs.customer import CustomerConfig
from crmpro.utils.pager import Pagination

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

    def start_time(self,obj = None,is_header = False):
        if is_header:
            return "开班时间"
        return obj.start_date.strftime("%Y-%m-%d")

    list_display = ["school",course_semester,num,start_time]
    show_add_btn = True
    edit_link = [course_semester,]

star.site.register(models.ClassList,ClassListConfig)


star.site.register(models.Customer,CustomerConfig)

class ConsultRecordConfig(star.StarkConfig):

    def get_date(self,obj=None,is_header=False):
        if is_header:
            return "最后跟进日期"
        return obj.date.strftime("%Y-%m-%d")


    list_display = ["customer","consultant",get_date]
    show_add_btn = True
    comb_filters = [
        star.FilterOption("customer")
    ]

    def changelist_view(self,request,*args,**kwargs):
        customer = request.GET.get("customer")

        # session 中获取当前用户ID

        current_login_user_id =  request.session.get (settings.LOGIN_INFO) ["user_id"]
        ct = models.Customer.objects.filter(consultant_id=current_login_user_id,id=customer).count()
        if not ct:
            return HttpResponse("别抢客户呀...")
        return super(ConsultRecordConfig,self).changelist_view(request,*args,**kwargs)
star.site.register(models.ConsultRecord,ConsultRecordConfig)

#老师上课记录
class CourseRecordConfig(star.StarkConfig):
    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url_list = [
            url(r'^(\d+)/score_list/$', self.wrapper(self.score_list), name="%s_%s_score_list" % app_model_name),
        ]
        return url_list

    def score_list(self, request, record_id):
        if request.method == "GET":
            data = []
            student_record_list = models.StudentRecord.objects.filter(course_record_id = record_id)
            #给每一个学习记录对象生成一个option 评分下拉框和一个评语text area
            for obj in student_record_list:
                TempForm = type("TempForm",(Form,),{
                    "score_%s"%obj.pk:fields.ChoiceField(choices=models.StudentRecord.score_choices,widget=widgets.Select(attrs={"class":"form-control"})),
                    "homework_note_%s"%obj.pk:fields.CharField(widget=widgets.Textarea(attrs={"rows":1,"cols":60,"class":"form-control"}))
                })
                data.append({"obj":obj,"form":TempForm(initial={"score_%s"%obj.pk:obj.score,"homework_note_%s"%obj.pk:obj.homework_note})})
            pager_obj = Pagination(request.GET.get('page', 1), len(data), request.path_info,request.GET)
            host_list = data[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()

            return render(request,"score_list.html",{"data":host_list,"page_html":html})
        else:
            data_dict = {}
            for key,value in request.POST.items():
                if key == "csrfmiddlewaretoken":
                    continue
                name,nid = key.rsplit("_",1)
                if nid in data_dict:
                    data_dict[nid][name] = value
                else:
                    data_dict[nid] = {name:value}
            for nid,update_dict in data_dict.items():
                models.StudentRecord.objects.filter(id=nid).update(**update_dict)
            return redirect(request.path_info)


    def attendance(self,obj = None,is_header = False):
        if is_header:
            return "考勤"
        return mark_safe("<a href='/stark/crm/studentrecord/?course_record=%s'>考勤管理</a>"%obj.pk)

    def display_score_list(self,obj = None,is_header = False):
        if is_header:
            return "成绩录入"
        #反向生成url
        url = reverse("stark:crm_courserecord_score_list",args=(obj.pk,))
        return mark_safe("<a href='%s'>成绩录入</a>"%url)



    list_display = ["class_obj","day_num",attendance,display_score_list]
    show_add_btn = True
    edit_link = ["class_obj"]
    show_actions = True



    def multi_init(self,request):
        """
        自定义学生上课记录初始化
        :param request:
        :return:
        """
        pk_list = request.POST.get("pk") #老师上课记录ID

        record_list = models.CourseRecord.objects.filter(id__in=pk_list)
        for record in record_list:
            exist = models.StudentRecord.objects.filter(course_record=record).exists()
            if exist:
                continue
            student_list = models.Student.objects.filter(class_list=record.class_obj)
            bulk_list = []
            for student in student_list:
                bulk_list.append(models.StudentRecord(student=student,course_record=record))
            models.StudentRecord.objects.bulk_create(bulk_list)


    multi_init.short_desc = "学生上课记录初始化"
    actions = [multi_init]
star.site.register(models.CourseRecord,CourseRecordConfig)

class StudentRecordConfig(star.StarkConfig):

    def display_record(self,obj = None,is_header = False):
        if is_header:
            return "考勤"
        return obj.get_record_display()
    list_display = ["course_record","student",display_record]

    comb_filters = [
        star.FilterOption("course_record")
    ]

    edit_link = ["course_record"]

    def action_checked(self,request):
        pk_list = request.POST.getlist("pk")
        models.StudentRecord.objects.filter(id__in=pk_list).update(record="checked")
    action_checked.short_desc = "签到"

    def action_vacate(self,request):
        pk_list = request.POST.getlist("pk")
        models.StudentRecord.objects.filter(id__in=pk_list).update(record="vacate")
    action_vacate.short_desc = "请假"

    def action_late(self,request):
        pk_list = request.POST.getlist("pk")
        models.StudentRecord.objects.filter(id__in=pk_list).update(record="late")
    action_late.short_desc = "迟到"

    def action_noshow(self,request):
        pk_list = request.POST.getlist("pk")
        models.StudentRecord.objects.filter(id__in=pk_list).update(record="noshow")
    action_noshow.short_desc = "缺勤"
    def action_leave_early(self,request):

        pk_list = request.POST.getlist("pk")
        models.StudentRecord.objects.filter(id__in = pk_list).update(record = "leave_early")
    action_leave_early.short_desc = "早退"

    actions = [action_checked,action_vacate,action_late,action_noshow,action_leave_early]
    show_actions = True


star.site.register(models.StudentRecord,StudentRecordConfig)

star.site.register(models.Student,StudentConfig)


class SaleRankConfig(star.StarkConfig):
    list_display = ["user","num","weight"]
    show_add_btn = True
star.site.register(models.SaleRank,SaleRankConfig)