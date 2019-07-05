from django.shortcuts import render
from django.http import HttpResponse
from common.models import Users
import pymysql
from tinydb.settings import DATABASES as db_config

#-----------数据库操作--------------#
def excute_sql(sqllist):
    try:
        #建立连接
        # 获得数据库信息
        host = db_config['default']['HOST']
        port = int(db_config['default']['PORT'])
        user = db_config['default']['USER']
        password = db_config['default']['PASSWORD']

        #建立连接
        conn = pymysql.connect(host=host, port=port, user=user, password=password, db='testdb', charset='utf8')
        cursor = conn.cursor()
        for sql in sqllist:
            cursor.execute(sql)

        # 提交修改，关闭连接，游标和连接都要关闭
        conn.commit()

    except Exception as err:
        conn.rollback()#表存在就回滚操作
        print(err)
        raise err
    finally:
        cursor.close()
        conn.close()

        
#--------------会员操作--------------#
# 浏览会员
def index(request):
    # 执行数据查询，并放置到模板中
    list = Users.objects.all()
    context = {"userslist":list}
    return render(request,'myadmin/users/index.html',context)


def add(request):
	return render(request,'myadmin/users/add.html')
  
def insert(request):
    try:
        ob = Users()
        ob.sid = request.POST['username']
        ob.state = request.POST['state']

        if ob.state == '':
            ob.state = 0

        ob.password = request.POST['password']
        
        ob.save()

        sqllist = []
        #根据用户id创建一个数据库
        sqllist.append(f'create database {ob.sid};')

        #给数据库创建一个用户
        if int(ob.state) == 0: #学生
            sqllist.append("create user {} identified by '{}';".format(ob.sid, request.POST['password']))
            sqllist.append("grant select on pub.* to {};".format(ob.sid))
            sqllist.append("grant drop, create, select, insert, update, delete on {}.* to {};".format(ob.sid, ob.sid))
            sqllist.append("flush privileges;")

        else:
            sqllist.append("create user {} identified by '{}';".format(ob.sid, request.POST['password']))
            sqllist.append("grant drop, create, select, insert, update, delete on testdb.* to {};".format(ob.sid))
            sqllist.append("grant all on pub.* to {};".format(ob.sid))
            sqllist.append("grant all on {}.* to {};".format(ob.sid, ob.sid))
            sqllist.append("flush privileges;")
        print(sqllist)

        excute_sql(sqllist)

        context = {'info':'添加成功！'}
    except Exception as err:
        print(err)
        context = {'info':'添加失败！'}

    return render(request,"myadmin/info.html",context)


def delete(request,uid):
    try:
        
        ob = Users.objects.get(id=uid)

        #删除对应的数据库
        sql1 = f'drop database {ob.sid};'
        sql2 = f'drop user {ob.sid}'
        excute_sql([sql1, sql2])

        #删除对象
        ob.delete()
        context = {'info':'删除成功！'}
    except:
        context = {'info':'删除失败！'}
    return render(request,"myadmin/info.html",context)

# 打开会员信息编辑表单
def edit(request, uid):
    try:
        ob = Users.objects.get(id=uid)
        context = {'user':ob}
        return render(request,"myadmin/users/edit.html",context)
    except Exception as err:
        print(err)
        context = {'info':'没有找到要修改的信息！'}
    return render(request,"myadmin/info.html",context)

def update(request,uid):
    try:
        ob = Users.objects.get(id=uid)
        ob.sid = request.POST['name']
        ob.state = request.POST['state']
        # 修改权限
        if ob.state == 0:
            # 回收访问testdb的权限
            sqllist = ["revoke drop, create, select, insert, update, delete on testdb.* to {};".format(ob.sid)]
        else:
            # 添加访问testdb的权限
            sqllist = ["grant drop, create, select, insert, update, delete on testdb.* to {};".format(ob.sid)] 
        sqllist.append("flush privileges;")
        excute_sql(sqllist)
        
        ob.save()
        context = {'info':'修改成功！'}
    except Exception as err:
        print(err)
        context = {'info':'修改失败！'}
    return render(request,"myadmin/info.html",context)


