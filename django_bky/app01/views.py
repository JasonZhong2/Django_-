import random
from io import BytesIO

from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
from app01.myforms import MyRegForm
from app01 import models

from django.http import JsonResponse

from PIL import Image,ImageDraw,ImageFont

from django.contrib import auth



def register(request):
    form_obj = MyRegForm()

    #Forbidden (CSRF token missing or incorrect.): /register/

    if request.method =='POST':
        back_dict = {'code': 200, 'msg': ''}
        #通过验证 自定义forms组件的验证
        form_obj = MyRegForm(request.POST)

        #校验数据是否合法
        if form_obj.is_valid():
            #通过校验的数据会以字典的形式返回字典
            clean_data = form_obj.cleaned_data
            #确认密码不需要插入到数据库
            clean_data.pop('confirm_password')
            #处理头像数据
            avatar = request.FILES.get('avatar')
            if avatar:
                clean_data['avatar'] = avatar
            #保存数据到数据库中
            # **clean_data 将字典打散成形参传入 键=值
            models.UserInfo.objects.create_user(**clean_data)
            #返回登录页面
            back_dict['url'] = '/login/'
        else:
            back_dict['code'] = 400
            #将报错信息添加字典中
            back_dict['msg'] = form_obj.errors

        return JsonResponse(back_dict)

    return render(request,'register.html',locals())

#登录
def login(request):

    if request.method == 'POST':
        back_dict = {'code': 200, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code').upper()
        #校验验证码是否正确
        session_code = request.session['code'].upper()
        if session_code == code:
            #校验用户数据是否正确
            user_obj = auth.authenticate(request,username=username,password=password)
            if user_obj:#用户名和密码正确
                #存储session 保存用户的登录状态
                auth.login(request,user_obj)
                back_dict['url'] = '/home/'
            else:
                back_dict['code'] = 401
                #将报错信息添加到字典中
                back_dict['msg'] = '用户名或密码错误'
        else:
            back_dict['code'] = 409
            # 将报错信息添加到字典中
            back_dict['msg'] = '验证码错误'

        return JsonResponse(back_dict)

    return render(request,'login.html')

#随机的颜色
def random_color():
    #自动转换成元组
    return random.randint(0,255),random.randint(0,255),random.randint(0,255)

#验证码
def get_code(request):

    #读取本地文件
    # with open('static/images/default.png', 'rb') as f:
    #     img_data = f.read()
    # return HttpResponse(img_data)
    # 这样会有问题?
    # 1 颜色是固定的
    # 2 没有文字
    # 3 难道每次生成图片都要用图片的文件来保存吗? 用内存解决
    # img_obj = Image.new('RGB',(380,33),'red').save('code.png')
    # with open('code.png', 'rb') as f:
    #     img_data = f.read()
    # return HttpResponse(img_data)
    img_obj = Image.new('RGB', (380, 33), random_color())
    img_draw = ImageDraw.Draw(img_obj) #生成画布（画笔）对象
    img_font = ImageFont.truetype('static/fonts/SegUIVar.ttf',28) #加载字体

    #生成随机验证码
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65,90)) #大写字母
        random_lower = chr(random.randint(97,122))#小写字母
        random_num = str(random.randint(0,9))#0-9数字
        #从上面这3个值当中随机绘制验证码
        random_char = random.choice([random_upper,random_lower,random_num])
        #绘制验证码
        #参数一： 坐标 x坐标 380/5=70左右 每个位置占40左右   y坐标就用 3
        #参数二： 随机产生的字符
        #参数三： 颜色
        #参数四： 字体
        img_draw.text((40+70*i,1),random_char,random_color(),img_font)

        code += random_char

    #把验证码保存到session当中
    request.session['code'] =code

    # 添加干扰线增强安全性
    for i in range(5):
        x1 = random.randint(0, 380)
        y1 = random.randint(0, 33)
        x2 = random.randint(0, 380)
        y2 = random.randint(0, 33)
        img_draw.line([(x1,y1),(x2,y2)],fill=random_color(),width=1)

    io_obj = BytesIO()
    img_obj.save(io_obj,'png')
    return HttpResponse(io_obj.getvalue()) #返回二进制数据给前端

#首页

def home(request):
    #查询所有的文章
    article_list = models.Article.objects.all()
    return render(request,'home.html',locals())

#登录验证装饰器
from django.contrib.auth.decorators import login_required

#修改密码
@login_required
def set_password(request):

    if request.method == 'POST':
        back_dict = {'code': 200, 'msg': ''}

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        #1 验证旧密码是否正确
        is_right = request.user.check_password(old_password)
        if is_right:
           #2 校验两次密码是否一致
            if new_password == confirm_password:
                request.user.set_password(new_password) #修改对象属性
                request.user.save()
            else:
                back_dict['code'] = 401
                back_dict['msg'] = '两次密码不一致'
        else:
            back_dict['code'] = 402
            back_dict['msg'] = '原密码错误'

        return JsonResponse(back_dict)

#退出登录
def logout(request):
    auth.logout(request)
    return redirect('/home/')

from django.db.models import Count
from django.db.models.functions import TruncMonth
#个人站点
def site(request,username,**kwargs):
    #kwargs: 以字典的形式接收多余的参数


    #先校验个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    #不存在这个站点
    if not user_obj:
        #返回404页面给你
        return render(request,'404.html')

    #  先通过用户拿到站点
    blog = user_obj.blog
    # 再通过站点 获取文章列表
    article_list = models.Article.objects.filter(blog=blog)
    if kwargs: #说明你是通过左侧菜单栏进入的 {'condition':'category','param':1}
        condition = kwargs.get('condition')
        param = kwargs.get('param')

        if condition == 'category':
            article_list = article_list.filter(category__pk=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__pk=param)
        elif condition == 'archive':
            year,month = param.split('-')
            article_list = article_list.filter(create_time__year=year,create_time__month=month)



    # #查询该用户的每个分类的文章数
    # category_list = models.Category.objects.filter(blog=blog).\
    #     annotate(count_num=Count('article__pk')).\
    #     values_list('name','count_num','pk')
    #
    # #查询该用户的标签数
    # tag_list = models.Tag.objects.filter(blog=blog).\
    #     annotate(count_num=Count('article__pk')).\
    #     values_list('name','count_num','pk')
    #
    # #查询该用户的日期归档
    # # 1 查询该用户所写的所有的文章
    # # 2 按照年月进行分组, 查询月份
    # # 3 按照月份进行分组 查询每个月的文章数
    # date_list = models.Article.objects.filter(blog=blog)\
    #     .annotate(mouth=TruncMonth('create_time')).values('mouth')\
    #     .annotate(count_num=Count('pk'))\
    #     .values_list('mouth','count_num')


    return render(request,'site.html',locals())

#文章详情
def article_detail(request,username,article_id):
    #查询文章对象本身
    article_obj = models.Article.objects.filter(pk=article_id,
                                  blog__user__username=username).first()

    if not article_obj:
        return render(request,'404.html')

    blog = article_obj.blog

    #获取评论的内容
    comment_list=models.Comment.objects.filter(article=article_obj)


    return render(request,'article_detail.html',locals())

import json
from django.db.models import F
#点赞点踩
def up_or_down(request):

    if request.method == 'POST':
        back_dict = {'code':200,'msg':''}

        # 判断该用户是否登录
        if request.user.is_authenticated:
            #文章id
            article_id = request.POST.get('article_id')
            #是否是点赞还是点踩
            is_up = request.POST.get('is_up')#字符串的布尔值
            #将JSON格式的字符串转成python的布尔值
            is_up=json.loads(is_up)
            # 判断当前文章是否是自己写的（如果是自己写的 无法给自己点赞）
            article_obj = models.Article.objects.filter(pk=article_id).first()
            #如果文章不属于当前用户呢?
            if not article_obj.blog.user == request.user:
                # 如果是否已经点赞过/点踩过 您已经支持过了
                is_click = models.UpOrDown.objects.filter(user=request.user,article=article_obj)
                #如果没查询到用户点赞/点踩记录就说明是第一次
                if not is_click:
                    # 操作数据库
                    if is_up: #点赞
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dict['msg'] = '点赞成功'
                    else: #点踩
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        back_dict['msg'] = '点踩成功'
                    #意味着我的点赞和点踩的数据你要拿到并且返回给前端
                    article_obj.refresh_from_db() #刷新对象
                    back_dict['up_num']=article_obj.up_num #点赞
                    back_dict['down_num'] =article_obj.down_num #点踩

                    #添加数据到点赞点踩表中
                    models.UpOrDown.objects.create(user=request.user,article=article_obj,is_up=is_up)
                else:#点赞或者点踩过了
                    back_dict['code'] = 401
                    back_dict['msg'] = '您已经支持过了'
            else:
                back_dict['code'] = 401
                back_dict['msg'] = '不能给自己点赞'
        else:
            back_dict['code'] = 402
            back_dict['msg'] = "请先<a href='/login/'>登录</a>"

        return JsonResponse(back_dict)
#评论
def comment(request):

    if request.method == 'POST':
        back_dict = {'code':200,'msg':''}
        #文章id
        article_id = request.POST.get('article_id')
        #评论的内容
        content = request.POST.get('content')
        #父id
        parentId = request.POST.get('parentId')


        #判断当前文章是否是自己写的 如果是自己写的 无法给自己评论
        article_obj = models.Article.objects.filter(pk=article_id).first()

        if not article_obj.blog.user == request.user:

            #保存评论数据到数据库,给文章表中的评论数+1
            models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)

            models.Comment.objects.create(user=request.user,
                                          article=article_obj,
                                          content=content,
                                          patent_id=parentId
                                          )
            back_dict['msg'] = '评论成功'
            #组装某某楼给我
            back_dict['comment_count'] = models.Comment.objects.filter(article=article_obj).count()
            #组装评论人的名字
            back_dict['username'] =request.user.username
            #评论的内容


        else:
            back_dict['code'] = 402
            back_dict['msg'] = '不能评论自己的文章'

        return JsonResponse(back_dict)