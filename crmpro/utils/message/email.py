#!/usr/bin/env python
#-*- coding:utf-8 -*-
#date:"2017-12-28,23:09"

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from .base import BaseMessage

class Email(BaseMessage):
    def __init__(self):
        self.email = "evday0815@sina.com"
        self.user = "evday0815@sina.com"
        self.pwd = "19910815@JIAJIA"

    def send(self,subject,body,to,name):

        msg = MIMEText(body,'plain','utf-8')

        msg["From"] = formataddr([self.user,self.email])

        msg["To"] = formataddr([name,to])
        msg["Subject"] = subject

        server = smtplib.SMTP("smtp.sina.com",25)
        server.login(self.email,self.pwd)
        server.sendmail(self.email,[to,],msg.as_string())

        server.quit()
