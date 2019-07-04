from django.shortcuts import render
from django.http import HttpResponse
from common.models import Users, Tests
from django.shortcuts import redirect
from django.core.urlresolvers import reverse


def index(request):
	return render(request, 'myadmin/index.html')

# ==============后台管理员操作====================
# 会员登录表单
def login(request):
    return render(request,'myadmin/login.html')

# 会员执行登录
def dologin(request):
    try:
        #根据账号获取登录者信息
        user = Users.objects.get(sid=request.POST['username'])
        #判断当前用户是否是后台管理员用户
        if user.state == 1:
            # 验证密码
            if user.password == request.POST['password']:
                # 此处登录成功，将当前登录信息放入到session中，并跳转页面
                request.session['adminuser'] = user.sid
                #print(json.dumps(user))
                return redirect(reverse('myadmin_index'))
            else:
                context = {'info':'登录密码错误！'}
        else:
            context = {'info':'此用户非后台管理用户！'}
    except Exception as err:
        context = {'info':'登录账号错误！'}
        print(err)
    return render(request,"myadmin/login.html",context)

# 会员退出
def logout(request):
    # 清除登录的session信息
    del request.session['adminuser']
    # 跳转登录页面（url地址改变）
    return redirect(reverse('myadmin_login'))

