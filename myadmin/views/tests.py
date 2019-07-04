from django.shortcuts import render
from django.http import HttpResponse
from common.models import Tests

# 浏览会员
def index(request):
    # 执行数据查询，并放置到模板中
    list = Tests.objects.all()
    context = {"userslist":list}
    return render(request,'myadmin/tests/index.html',context)


def add(request):
	return render(request,'myadmin/tests/add.html')
  
def insert(request):
    try:
        ob = Tests()
        ob.name = request.POST['name']
        ob.content = request.POST['content']
        ob.answer = request.POST['answer']
        ob.save()
        context = {'info':'添加成功！'}
    except Exception as err:
        print(err)
        context = {'info':'添加失败！'}

    return render(request,"myadmin/info.html",context)


def delete(request,uid):
    try:
        ob = Tests.objects.get(id=uid)
        ob.delete()
        context = {'info':'删除成功！'}
    except:
        context = {'info':'删除失败！'}
    return render(request,"myadmin/info.html",context)

# 打开会员信息编辑表单
def edit(request, uid):
    try:
        ob = Tests.objects.get(id=uid)
        context = {'user':ob}
        return render(request,"myadmin/tests/edit.html",context)
    except Exception as err:
        print(err)
        context = {'info':'没有找到要修改的信息！'}
    return render(request,"myadmin/info.html",context)

def update(request,uid):
    try:
        ob = Tests.objects.get(id=uid)
        ob.content = request.POST['content']
        ob.answer = request.POST['answer']
        ob.save()
        context = {'info':'修改成功！'}
    except Exception as err:
        print(err)
        context = {'info':'修改失败！'}
    return render(request,"myadmin/info.html",context)