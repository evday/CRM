from django.db import models






class User(models.Model):
    '''
    用户表
    '''
    username = models.CharField(verbose_name="用户名",max_length=32)
    password = models.CharField(verbose_name="密码",max_length=32)
    email = models.EmailField(verbose_name="邮箱",max_length=32)

    roles = models.ManyToManyField(to="Roles",verbose_name="用户角色",blank=True)

    class Meta:
        verbose_name_plural = "用户表"

    def __str__(self):
        return self.username

class Roles(models.Model):
    '''
    角色表
    '''
    title = models.CharField(verbose_name="角色",max_length=32)
    permissions = models.ManyToManyField(to="Permission",verbose_name="角色权限")

    class Meta:
        verbose_name_plural = "角色表"
    def __str__(self):
        return self.title

class Permission(models.Model):
    '''
    权限表
    '''
    title = models.CharField(verbose_name="权限",max_length=32)
    url = models.CharField(verbose_name="含正则的url",max_length=64)
    # is_menu = models.BooleanField(verbose_name="是否是菜单")
    menu_gp = models.ForeignKey(verbose_name="组内菜单",to='self',null=True,blank=True)
    code = models.CharField(verbose_name="代码",max_length=16)
    group = models.ForeignKey(verbose_name="所属组",to="Group")


    class Meta:
        verbose_name_plural = "权限表"

    def __str__(self):
        return self.title

class Group(models.Model):
    '''
    权限组
    '''
    caption = models.CharField(verbose_name="组名称",max_length=16)
    menu = models.ForeignKey(to="Menu",verbose_name="所属菜单")

    def __str__(self):
        return self.caption

class Menu(models.Model):
    '''
    菜单组
    '''
    title = models.CharField(verbose_name="菜单名",max_length=16)

    def __str__(self):
        return self.title
