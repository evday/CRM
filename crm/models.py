from django.db import models
from rbac import models as rbac_model
# Create your models here.

class Department(models.Model):
    '''
    部门表
    '''

    title = models.CharField(max_length=16,verbose_name="部门名称")
    code = models.IntegerField(verbose_name="部门编号",unique=True,null=True)

    def __str__(self):
        return self.title

class UserInfo(models.Model):
    '''
    员工表
    '''
    auth = models.OneToOneField(verbose_name = "用户权限",to = rbac_model.User,null = True,blank = True)
    name = models.CharField(max_length=16,verbose_name="员工姓名")
    username = models.CharField(max_length=32,verbose_name="用户名")
    password = models.CharField(max_length=64,verbose_name="密码")
    email = models.EmailField(max_length=64,verbose_name="邮箱")

    depart = models.ForeignKey(verbose_name="部门",to="Department",to_field="code")

    def __str__(self):
        return self.name

class Course(models.Model):
    '''
    课程表
    '''
    name = models.CharField(max_length=32,verbose_name="课程名称")

    def __str__(self):
        return self.name

class School(models.Model):
    '''
    校区表
    '''
    title = models.CharField(max_length=32,verbose_name="校区名称")

    def __str__(self):
        return self.title

class ClassList(models.Model):
    '''
    班级表
    '''
    school = models.ForeignKey(verbose_name="校区",to="School")
    course = models.ForeignKey(verbose_name="课程名称",to="Course")

    semester = models.IntegerField(verbose_name="班级(期)")
    price = models.IntegerField(verbose_name="学费")
    start_date = models.DateField(verbose_name="开班日期")
    graduate_date = models.DateField(verbose_name="结业日期",null=True,blank=True)
    memo = models.CharField(verbose_name="说明",max_length=255,null=True,blank=True)

    teachers = models.ManyToManyField(verbose_name="任课老师",to="UserInfo",related_name='teach_classes',limit_choices_to={"depart_id__in":[1003,1004]})
    tutor = models.ForeignKey(verbose_name="班主任",to="UserInfo",related_name="classes",limit_choices_to={"depart_id":1002})

    def __str__(self):
        return "{0}{1}期".format(self.course.name,self.semester)

class Customer(models.Model):
    '''
    客户表
    '''
    qq = models.CharField(verbose_name="qq",max_length=32,unique=True,help_text="QQ号必须唯一")
    name = models.CharField(verbose_name="学生姓名",max_length=16)
    gender_choices = ((1,"男"),(2,"女"))
    gender = models.SmallIntegerField(verbose_name="性别",choices=gender_choices)

    education_choices = (
        (1, '重点大学'),
        (2, '普通本科'),
        (3, '独立院校'),
        (4, '民办本科'),
        (5, '大专'),
        (6, '民办专科'),
        (7, '高中'),
        (8, '其他')
    )

    education = models.IntegerField(verbose_name="学历",choices=education_choices,blank=True,null=True)
    graduation_school = models.CharField(verbose_name="毕业学校",max_length=32,blank=True,null=True)
    major = models.CharField(verbose_name="所学专业",max_length=32,blank=True,null=True)

    experience_choices = [
        (1, '在校生'),
        (2, '应届毕业'),
        (3, '半年以内'),
        (4, '半年至一年'),
        (5, '一年至三年'),
        (6, '三年至五年'),
        (7, '五年以上'),
    ]

    experience = models.IntegerField(verbose_name="工作经验",blank=True,null=True,choices=experience_choices)

    work_status_choices = [
        (1, '在职'),
        (2, '无业')
    ]
    work_status = models.IntegerField(verbose_name="职业状态",choices=work_status_choices,default=1,blank=True)

    company = models.CharField(verbose_name="目前就职公司",max_length=64,blank=True,null=True)
    salary = models.CharField(verbose_name="当前薪资",max_length=64,blank=True,null=True)

    source_choices = [
        (1, "qq群"),
        (2, "内部转介绍"),
        (3, "官方网站"),
        (4, "百度推广"),
        (5, "360推广"),
        (6, "搜狗推广"),
        (7, "腾讯课堂"),
        (8, "广点通"),
        (9, "高校宣讲"),
        (10, "渠道代理"),
        (11, "51cto"),
        (12, "智汇推"),
        (13, "网盟"),
        (14, "DSP"),
        (15, "SEO"),
        (16, "其它"),
    ]

    source = models.IntegerField(verbose_name="客户来源",choices=source_choices,default=1)
    #自关联
    referral_form = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        verbose_name="转介绍学员",
        help_text="若此客户是转介绍自内部学员,请在此处选择内部学员姓名",
        related_name="internal_referral"

    )

    course = models.ManyToManyField(verbose_name="咨询课程",to="Course")

    status_choices = [
        (1,"已报名"),
        (2,"未报名")
    ]

    status = models.IntegerField(
        verbose_name="状态",
        choices=status_choices,
        default=2,
        help_text="选择客户此时的状态"
    )

    consultant = models.ForeignKey(verbose_name="课程顾问",to="UserInfo",related_name="consultant",limit_choices_to={"depart_id":1001})
    date = models.DateField(verbose_name="咨询日期",auto_now_add=True)
    recv_date = models.DateField(verbose_name='接客时间', null=True, blank=True)
    last_consult_date = models.DateField(verbose_name="最后跟进日期",auto_now_add=True)

    def __str__(self):
        return "姓名：{0},QQ{1}".format(self.name,self.qq)

class CustomerDistribution(models.Model):
    '''
    客户分配表
    '''
    user = models.ForeignKey(verbose_name = "课程顾问",to = 'UserInfo',related_name = "course_teacher",limit_choices_to = {"depart_id":1002})
    customer = models.ForeignKey(verbose_name = "客户",to = "Customer",related_name = "dealers")
    create_time = models.DateField()
    status_choices = (
        (1,"正在跟单"),
        (2,"已成单"),
        (3,"3天未跟进"),
        (4,"15天未成单"),
    )
    status = models.IntegerField(verbose_name = "状态",choices = status_choices,default = 1)
    memo = models.CharField(verbose_name = "备注",max_length = 255)



class SaleRank(models.Model):
    '''
    销售权重表
    '''
    user = models.ForeignKey(to = "UserInfo",limit_choices_to = {"depart_id":1001},verbose_name = "姓名")
    num = models.IntegerField(verbose_name = "每日可转化数量")
    weight = models.IntegerField(verbose_name = "权重")

class ConsultRecord(models.Model):
    '''
    客户跟进记录
    '''
    customer = models.ForeignKey(verbose_name="所咨询客户",to="Customer")
    consultant = models.ForeignKey(verbose_name="跟进人",to="UserInfo")
    date = models.DateField(verbose_name="跟进日期",auto_now_add=True)
    note = models.TextField(verbose_name="跟进内容.....")

class PaymentRecord(models.Model):
    '''
    缴费记录
    '''
    customer = models.ForeignKey(Customer,verbose_name="客户")
    class_list= models.ForeignKey(verbose_name="班级",to="ClassList",blank=True,null=True)

    pay_type_choices = [
        (1, "订金/报名费"),
        (2, "学费"),
        (3, "转班"),
        (4, "退学"),
        (5, "退款"),
    ]

    pay_type = models.IntegerField(verbose_name="费用类型",choices=pay_type_choices,default=1)
    paid_fee = models.IntegerField(verbose_name="费用数额",default=0)
    turnover = models.IntegerField(verbose_name="成交金额",blank=True,null=True)
    quote = models.IntegerField(verbose_name="报价金额",blank=True,null=True)
    note = models.TextField(verbose_name="备注",blank=True,null=True)
    date = models.DateTimeField(verbose_name="交款日期",auto_now_add=True)
    consultant = models.ForeignKey(verbose_name="负责老师",to="UserInfo",related_name="谁签的单就选谁")

class Student(models.Model):
    '''
    学生表(已报名）
    '''
    customer = models.OneToOneField(verbose_name="客户信息",to='Customer')

    username = models.CharField(verbose_name="用户名",max_length=32)
    password = models.CharField(verbose_name="密码",max_length=64)
    emergency_contract = models.CharField(verbose_name="紧急联系人",max_length=32,blank=True,)
    class_list = models.ManyToManyField(verbose_name="已报班级",to="ClassList",blank=True)

    company = models.CharField(verbose_name="公司",max_length=128,blank=True,null=True)
    location = models.CharField(verbose_name="所在区域",max_length=64,blank=True,null=True)
    position = models.CharField(verbose_name="岗位",max_length=64,blank=True,null=True)
    salary= models.IntegerField(verbose_name="薪资",blank=True,null=True)
    welfare = models.CharField(verbose_name="福利",max_length=256,blank=True,null=True)
    date = models.DateTimeField(verbose_name="入职时间",help_text="格式yyyy-mm-dd",auto_now_add=True)
    memo =  models.CharField(verbose_name="备注",max_length=256,blank=True,null=True)

    def __str__(self):
        return self.username

class CourseRecord(models.Model):
    '''
    上课记录
    '''
    class_obj = models.ForeignKey(verbose_name="班级",to="ClassList")
    day_num = models.IntegerField(verbose_name="节次",help_text="此处填写第几节课或第几天课程...,必须为数字")
    teacher = models.ForeignKey(verbose_name="讲师",to="UserInfo")
    date = models.DateField(verbose_name="上课日期",auto_now_add=True)

    course_title = models.CharField(verbose_name="本节课程标题",max_length=64,blank=True,null=True)
    course_memo = models.TextField(verbose_name="本节内容概要",null=True,blank=True)
    has_homework = models.BooleanField(verbose_name="有无作业",default=True)
    homework_title = models.CharField(verbose_name="本节作业标题",max_length=64,blank=True,null=True)
    exam = models.TextField(verbose_name="采分点",max_length=300,null=True,blank=True)

    def __str__(self):
        return "{0} day{1}".format(self.class_obj,self.day_num)

class StudentRecord(models.Model):
    '''
    学员上课记录
    '''
    course_record = models.ForeignKey(verbose_name="第几天课程",to="CourseRecord")
    student = models.ForeignKey(verbose_name="学员",to="Student")
    record_choices = (
        ('checked', "已签到"),
        ('vacate', "请假"),
        ('late', "迟到"),
        ('noshow', "缺勤"),
        ('leave_early', "早退"),
    )
    record = models.CharField(verbose_name="上课记录",choices=record_choices,default="checked",max_length=64)
    score_choices = (
        (100, 'A+'),
        (90, 'A'),
        (85, 'B+'),
        (80, 'B'),
        (70, 'B-'),
        (60, 'C+'),
        (50, 'C'),
        (40, 'C-'),
        (0, ' D'),
        (-1, 'N/A'),
        (-100, 'COPY'),
        (-1000, 'FAIL'),
    )
    score = models.IntegerField(verbose_name="本节成绩",choices=score_choices,default=-1)
    homework_note = models.CharField(verbose_name="作业评语",max_length=255,blank=True,null=True)
    note = models.CharField(verbose_name="备注",max_length=255,null=True,blank=True)

    homework = models.FileField(verbose_name="作业文件",blank=True,null=True,default=None)
    stu_memo = models.TextField(verbose_name="学员备注",blank=True,null=True)
    date = models.DateTimeField(verbose_name="提交作业时间",auto_now_add=True)

    def __str__(self):
        return "{0}-{1}".format(self.course_record,self.student)