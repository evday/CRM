#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-26,18:32"
import json

from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import reverse,HttpResponse,render

from stark.service import star
from crm.models import Student,StudentRecord


class StudentConfig(star.StarkConfig):

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label,self.model_class._meta.model_name)
        url_list = [
            url(r'^(\d+)/sv/$', self.wrapper(self.score_view), name="%s_%s_sv" % app_model_name),
            url(r'^chart/$', self.wrapper(self.scores_chart), name="%s_%s_chart" % app_model_name),
        ]
        return url_list

    def score_view(self,request,sid):
        stu_obj = Student.objects.filter(id=sid).first()
        if not stu_obj:
            return HttpResponse("查无此人")
        class_list = stu_obj.class_list.all()

        return render(request,'score_view.html',{"class_list":class_list,"sid":sid})

    def scores_chart(self,request):
        ret = {"status":False,"data":None,"msg":None}
        try:
            cid = request.GET.get("cid")
            sid = request.GET.get("sid")
            print(cid,sid,'&&&&&&&&&&&&&&')
            record_list = StudentRecord.objects.filter(student_id = sid,course_record__class_obj_id = cid).order_by("course_record_id")

            data = []
            for row in record_list:
                day = "day%s"%row.course_record.day_num
                data.append([day,row.score])
            ret["data"] = data
            ret["status"] = True


        except Exception as e:
            ret["msg"] = "获取失败"

        return HttpResponse(json.dumps(ret))

    def display_scores(self,obj = None,is_header = False):
        if is_header:
            return '查看成绩'
        url = reverse("stark:crm_student_sv",args=(obj.pk,))
        return mark_safe("<a href='%s'>点击查看</a>"%url)


    edit_link = ["username"]
    list_display = ["username","emergency_contract",display_scores]