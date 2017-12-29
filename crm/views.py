import json

from django.shortcuts import render,HttpResponse
from crm import models
from django.conf import settings
# Create your views here.
def login(request):
    if request.method == "GET":
        return render(request, "login.html")

    elif request.is_ajax():

        state = {"state": None}
        username = request.POST.get("user")

        if username == "":
            state["state"] = "user_none"
            return HttpResponse(json.dumps(state))
        password = request.POST.get("pwd")

        if password == "":
            state["state"] = "pwd_none"
            return HttpResponse(json.dumps(state))

        user = models.UserInfo.objects.filter(username=username, password=password).first()
        if user:
            state["state"] = "login_success"
            request.session[settings.LOGIN_INFO] = {"user_id":user.id,"username":user.username}

        else:
            state["state"] = "failed"

        return HttpResponse(json.dumps(state))

def index(request):
    return HttpResponse("登录成功")