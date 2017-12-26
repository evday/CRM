#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-21,16:28"

from django.template import Library
from django.urls import reverse
from django.db.models import DateField

from stark.service.star import site

from django.forms.boundfield import BoundField

register = Library()

@register.inclusion_tag("stark/form.html")
def form(config,model_form_obj):
    '''
    自定义标签，处理popup
    :param model_form_obj:
    :return:
    '''
    print(type(config),'==================')
    new_form = []
    for bfield in model_form_obj:  #这里的

        temp = {"is_popup":False,"item":bfield,"is_date":False}
        from django.forms.models import ModelChoiceField
        if isinstance(bfield.field,ModelChoiceField):
            related_class_name = bfield.field.queryset.model  #根据字段找多啊表名
            if related_class_name in site._registry: #说明是注册到stark.py 中的
                app_model_name = related_class_name._meta.app_label,related_class_name._meta.model_name

                #当前字段所在的类名related_name
                _model_name = config.model_class._meta.model_name #类名
                _related_name = config.model_class._meta.get_field(bfield.name).rel.related_name

                base_url = reverse("stark:%s_%s_add"%app_model_name) #拼接页面路径
                popurl = "%s?_popbackid=%s&model_name=%s&related_name=%s"%(base_url,bfield.auto_id,_model_name,_related_name)
                temp["is_popup"] = True
                temp["popup_url"] = popurl

        if  type(bfield.field).__name__ == "DateField":
            bfield.field.widget_attrs("is_date")
            temp["is_date"] = True
        new_form.append(temp)
    return {"form":new_form}



