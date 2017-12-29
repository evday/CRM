#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-27,9:28"
import datetime


from django.utils.safestring import mark_safe
from django.shortcuts import redirect,HttpResponse,render
from django.conf.urls import url
from django.db.models import Q
from django.conf import settings
from django.db import transaction

from stark.service import star
from crm import models
from crmpro.utils.pager import Pagination
from crm.form import SingleForm
from crmpro.utils import message


class CustomerConfig(star.StarkConfig):

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
        return mark_safe("<a href='/stark/crm/consultrecord/?customer=%s'>查看跟进记录</a>"%(obj.pk))


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
            url(r'^(\d+)/(\d+)/dc/$',self.wrapper(self.delete_course),name="%s_%s_dc"%app_model_name),
            url(r'^public/$',self.wrapper(self.public_view),name="%s_%s_public"%app_model_name),
            url(r'^(\d+)/competition/$',self.wrapper(self.competition_view),name="%s_%s_competition"%app_model_name),
            url(r'^user/$',self.wrapper(self.user_view),name="%s_%s_user"%app_model_name),
            url(r'^single/$',self.wrapper(self.single_view),name="%s_%s_user"%app_model_name),
        ]
        return patterns

    def public_view(self,request):
        '''
        公共客户资源
        :param request:
        :return:
        '''
        # 未报名 并且 (15天未成单(当前时间-15>接客时间) 或者 3 天未跟进(当前时间-3>最后跟进时间))

        current_date = datetime.datetime.now().date()
        no_deal = current_date - datetime.timedelta(days=15)
        no_follow = current_date - datetime.timedelta(days=3)
        # res = Q()
        # con = Q()
        # q1 = Q()
        # q1.children.append(("status",2),)
        # q2 = Q()
        # q2.children.append(("recv_date__lt",no_deal),)
        # q3 = Q()
        # q3.children.append(("last_consult_date__lt",no_follow))
        # con.add(q2,"OR")
        # con.add(q3,"OR")
        # res.add(q1,"AND")
        # res.add(con,"AND")
        # customer_list = models.Customer.objects.filter(res)
        customer_list = models.Customer.objects.filter(Q(recv_date__lt=no_deal)|Q(last_consult_date__lt=no_follow),status=2)

        pager_obj = Pagination ( request.GET.get ( 'page' , 1 ) , len ( customer_list ) , request.path_info ,request.GET)
        host_list = customer_list [ pager_obj.start :pager_obj.end ]
        html = pager_obj.page_html ()
        return render(request,'public_view.html',{'customer_list':host_list,"page_html":html})

    def competition_view(self,request,cid):

        '''
        继续跟进
        :return:
        '''
        #修改客户表,recv_time,last_consult_date,consultant
        #原课程顾问不是当前登录用户，必须是未报名，且3天未跟进或者15天未成单
        current_user_id = request.session.get(settings.LOGIN_INFO)["user_id"]


        current_date = datetime.datetime.now().date()
        no_deal = current_date - datetime.timedelta ( days = 15 )
        no_follow = current_date - datetime.timedelta ( days = 3 )

        row_count = models.Customer.objects.filter ( Q ( recv_date__lt = no_deal ) | Q ( last_consult_date__lt = no_follow ) ,status = 2,id=cid ).exclude(consultant_id=current_user_id).update(recv_date = current_date,last_consult_date=current_date,consultant_id=current_user_id)

        if not row_count:
            return HttpResponse("跟进失败")
        models.CustomerDistribution.objects.create(user_id=current_user_id,customer_id=cid,create_time=current_date)
        return HttpResponse("跟进成功")

    def user_view(self,request):
        '''
        当前登录销售的所有客户
        :param request:
        :return:
        '''
        current_user_id = request.session.get (settings.LOGIN_INFO) ["user_id"]
        customers = models.CustomerDistribution.objects.filter(user_id=current_user_id).order_by("-status")

        pager_obj = Pagination (request.GET.get ('page',1),len (customers),request.path_info,request.GET)
        host_list = customers [pager_obj.start:pager_obj.end]
        html = pager_obj.page_html ()
        return render(request,'user_view.html',{"customers":host_list,"page_html":html})

    def single_view(self,request):
        """
        单条录入客户数据,request.POST获取所有导入数据
        一，数据校验
        二，获取销售ID(完成自动分配)
        三，写入数据库
        :param request:
        :return:
        """
        if request.method == "GET":
            form = SingleForm()
            return render(request,"single_view.html",{"form":form})
        else:
            form = SingleForm(request.POST)
            #数据校验
            if form.is_valid():
                from crm.weight import AutoSale
                current_time = datetime.datetime.now().date()

                #获取销售ID
                sale_id = AutoSale.get_sale_id()
                sale_obj = models.UserInfo.objects.filter (id = sale_id).first ()

                if not sale_id:
                    return HttpResponse("无销售顾问，无法进行自动分配")

                try:
                    with transaction.atomic():
                        #创建客户表
                        form.instance.consultant_id = sale_id
                        form.instance.recv_date = current_time
                        form.instance.last_consult_date = current_time
                        new_customer = form.save()

                        #创建客户分配表
                        models.CustomerDistribution.objects.create(customer=new_customer,user_id=sale_id,create_time=current_time)

                        #发送提示消息
                        message.send_message('你别走了','三个月工资太多了',sale_obj.email,sale_obj.name)

                except Exception as e:
                    #创建客户或者分配销售异常
                    AutoSale.rollback(sale_id)
                    return HttpResponse("录入异常")
                return HttpResponse("录入成功")
            else:
                return render(request,'single_view.html',{"form":form})



