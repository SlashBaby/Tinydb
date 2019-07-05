from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator

from common.models import Users, Tests
from django.views.decorators.csrf import csrf_exempt
import pymysql
import json
from tinydb.settings import DATABASES as db_config


# ==============商品信息============== #
def index(request):
    '''项目前台首页'''
    return render(request,"web/index.html")

def lists(request,pIndex=1):

    '''商品列表页(搜索&分页)'''
    #判断是否登陆
    if not request.session.has_key('vipuser'):
        return redirect(reverse('login'))
    uid = request.session['vipuser']['id']
    context = {}

    # 获得数据库信息
    host = db_config['default']['HOST']
    port = int(db_config['default']['PORT'])
    user = db_config['default']['USER']
    password = db_config['default']['PASSWORD']

    #建立连接
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db='testdb', charset='utf8')
    cursor = conn.cursor()

    #获取商品信息查询对象
    list = Tests.objects.all()

    #给每一个试题对象添加一个index，并且计算状态
    for i, v in enumerate(list):
        v.state = _compute_state(uid, v.id, cursor)
        v.index = i + 1
        v.save()

    #封装信息加载模板输出
    context['testlist'] = list
    return render(request,"web/list.html",context)

def detail(request, gid):
    '''商品详情页'''
    #加载商品详情信息
    context = {}

    #判断gid是否越界
    maxindex = len(Tests.objects.all())
    if int(gid) < 1:
        gid = 1
    if int(gid) > maxindex:
        gid = maxindex

    #获得范围内的题目
    ob = Tests.objects.get(index=gid)
    context['goods'] = ob
    return render(request,"web/detail.html",context)

@csrf_exempt
def result(request, gid):
    '''返回结果'''
    if request.method == "POST":
        sql = request.POST.get('sql')
        sqllist = sql.split(';')
        if(sqllist[-1] == ''):
            sqllist = sqllist[:-1]
        res = excute_sql(sqllist, request)
    return JsonResponse(res)

# ==============前台会员登录====================
def login(request):
    '''会员登录表单'''
    return render(request,'web/login.html')

def dologin(request):
    '''会员执行登录'''
    try:
        #根据账号获取登录者信息
        user = Users.objects.get(sid=request.POST['username'])
        
        #判断当前用户是否是后台管理员用户
        if user.state == 0 or user.state == 1:
            # 验证密码
            if user.password == request.POST['password']:
                # 此处登录成功，将当前登录信息放入到session中，并跳转页面
                request.session['vipuser'] = user.toDict()
                return redirect(reverse('index'))
            else:
                context = {'info':'登录密码错误！'}
        else:
            context = {'info':'此用户为非法用户！'}
    except:
        context = {'info':'登录账号错误！'}
    return render(request,"web/login.html",context)

def logout(request):
    '''会员退出'''
    # 清除登录的session信息
    del request.session['vipuser']
    # 跳转登录页面（url地址改变）
    return redirect(reverse('index'))


#===============一些私有函数================#
def _compute_state(uid, tid, cursor):
    '''计算每个人每道题的成绩'''
    try:
        sql = 'select state from testdb.score where uid = {} and tid = {}'.format(uid, tid)
        cursor.execute(sql)
        table = [row for row in cursor.fetchall()]
        return table[0][0]
    except Exception as err:
        '''如果不存在的话，那么table[0]就会报错'''
        print(err)
        return 2


def excute_sql(sqllist, request):
    '''执行sql语句'''
    context = {}
    try:
        #获得用户id
        uid = request.session['vipuser']['id']

        #获得用户密码
        user = Users.objects.get(id=uid)
        username = user.sid
        dbname = user.sid
        password = user.password
        host = db_config['default']['HOST']
        port = int(db_config['default']['PORT'])

        #建立连接
        conn = pymysql.connect(host=host, port=port, user=username, password=password, db=dbname, charset='utf8')
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        #执行语句并且放回结果
        tablelist = []
        for sql in sqllist:
            cursor.execute(sql)
            table = [row for row in cursor.fetchall()]
            tablelist.append(table)

        # 提交修改，关闭连接，游标和连接都要关闭
        conn.commit()

        #设置放回结果
        context['ok'] = 1 # 表示sql语句执行成功
        context['result'] = tablelist
    except Exception as err:
        print(err, '*' * 10)
        context['ok'] = 0 # 表示sql语句执行失败
        conn.rollback()#表存在就回滚操作
    finally:
        cursor.close()
        conn.close()
        return context

@csrf_exempt
def judge(request, gid):
    '''root账户判断结果是否正确'''
    context = {}
    try:
        ob = Tests.objects.get(id=gid)
        tablename = ob.name


        # 获得用户数据库的名字
        uid = request.session['vipuser']['id']
        dbname = request.session['vipuser']['sid']

        # 获得root数据库信息
        host = db_config['default']['HOST']
        port = int(db_config['default']['PORT'])
        user = db_config['default']['USER']
        password = db_config['default']['PASSWORD']

        #建立连接
        conn = pymysql.connect(host=host, port=port, user=user, password=password, db='testdb', charset='utf8')
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

        #获得标准执行结果
        sql = ob.answer
        result = cursor.execute(sql) #执行sql语句，返回sql查询成功的记录数目
        table1 = [json.dumps(row) for row in cursor.fetchall()]

        #获得用户执行结果
        sql = 'select * from {}.{};'.format(dbname, tablename)
        result = cursor.execute(sql) #执行sql语句，返回sql查询成功的记录数目
        table2 = [json.dumps(row) for row in cursor.fetchall()]
        
        #更新结果'''
        if is_equal(table1, table2):
            update_score(cursor, uid, gid, 1);
            context['ok'] = 1
        else:
            update_score(cursor, uid, gid, 0);
            context['ok'] = 0

        # 提交修改，关闭连接，游标和连接都要关闭
        conn.commit()
    except Exception as err:
        context['ok'] = 2
        conn.rollback()#表存在就回滚操作
        print(err)
    finally:
        #关闭连接并且返回结果
        cursor.close()
        conn.close()
        return JsonResponse(context)

def is_equal(t1, t2):
    '''判断两张表是否相等'''
    set1 = set(t1)
    set2 = set(t2)
    if len(set1.difference(set2)) == 0:
        return True
    else:
        return False

def update_score(cursor, uid, gid, state):
    '''更新得分'''
    sql = 'select * from testdb.score where uid={} and tid={}'.format(uid, gid)
    result = cursor.execute(sql)
    if not result == 0:
        sql = 'update testdb.score set state={} where uid={} and tid={}'.format(state, uid, gid)
        cursor.execute(sql)
    else:
        sql = 'insert into testdb.score(tid,uid,state) values({},{},{})'.format(gid, uid, state)
        cursor.execute(sql)

        
        
    

