#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-28,18:30"
from django.forms import ModelForm

from crm import models

class SingleForm(ModelForm):
    class Meta:
        model = models.Customer
        exclude = ["consultant","status","recv_date","last_consult_date"]