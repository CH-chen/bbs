from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse

from blog import models
from blog import forms
from PIL import Image,ImageDraw,ImageFont
import random
from django.contrib import auth
from django.db.models import Count



# 自己生成验证码的登录
def login(request):
    # if request.is_ajax():  # 如果是AJAX请求
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        valid_code = request.POST.get("valid_code")  # 获取用户填写的验证码
        print(valid_code)
        print("用户输入的验证码".center(120, "="))
        if valid_code and valid_code.upper() == request.session.get("valid_code", "").upper():
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    return render(request, "login.html")

def logout(request):
    auth.logout(request)
    return redirect("/index/")

def register(request):

    reform_obj = forms.RegForm()
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        reform_obj = forms.RegForm(request.POST)
        print(request.POST)
        if reform_obj.is_valid():
            del reform_obj.cleaned_data['re_password']
            # reform_obj.cleaned_data.pop('re_password')
            avatar_img = request.FILES.get("avatar")
            user = models.UserInfo.objects.create_user(**reform_obj.cleaned_data,avatar=avatar_img)


            ret['msg'] = '/index/'
            auth.login(request,user)
            return JsonResponse(ret)
        else:
            print(reform_obj.errors)
            ret['status'] = 1
            ret['msg'] = reform_obj.errors
            print('='*50)
            print(ret)

            return JsonResponse(ret)

    return render(request,'register.html',{'reform_obj':reform_obj})

def index(request):
    article_list = models.Article.objects.all()
    return render(request, 'index.html', {"article_list": article_list})
def home(request,username):
    #取出用户对象
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    #取出用户的文章列表
    article_list = models.Article.objects.filter(user=user) #一对多第一种正向查询
    print(user)
    print(user.blog.nid)
    print(user.blog.category_set.all()) #这是一个列表对象，要用for循环遍历
    #一对一
    print(user.blog.title)
    print(user.article_set.all())
    #一对多第二种反向查询
    for i in user.article_set.all():
        print(i.title)
        print("======")
        print(i.desc)
    #分类的文章数量
    blog = user.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title","c")

    #标签下的文章数量
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title","c")
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym":"date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym","c")


    return render(request,'home.html',
                  {"user":user,
                   "username":username,
                   'article_list':article_list,
                   'category_list':category_list,
                   "tag_list":tag_list,
                   "archive_list":archive_list,
                                       })
def category_article(request,username,category_title):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    category_article = models.Article.objects.filter(category__title=category_title).filter(user=user)
    for article_list in category_article:
        print(article_list)
    print("++++++")

    return render(request,"category_list.html",
                  {
                      "user": user,
                      "blog":blog,
                      "username":username,

                      "category_article":category_article
                  })

def get_left(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    # 标签下的文章数量
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")
    return category_list,tag_list,archive_list

def article_detail(request,username,pk):
    print(pk)#获取浏览器中的用户名和id值
    print("============")
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    article_obj = models.Article.objects.filter(pk=pk).first()
    # category_list,tag_list,archive_list = get_left(username)
    comment_list = models.Comment.objects.filter(article_id=pk)
    return render(request,'detail.html',
                  {"article":article_obj,
                   "user":user,
                   "blog":blog,
                   "username":username,
                   "comment_list": comment_list,
                   # 'category_list': category_list,
                   # "tag_list": tag_list,
                   # "archive_list": archive_list,
                   })
import json
from django.db.models import F

def up_down(request):
    print(request.POST)
    ret = {"state":True,}

    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))
    print(is_up)
    user = request.user
    print(user)
    try:
        models.ArticleUpDown.objects.create(article_id=article_id,user=user,is_up=is_up)
        if is_up:

            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
        else:
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    except Exception as e:
        ret["state"] = False
        ret["first_action"] = models.ArticleUpDown.objects.filter(article_id=article_id,user=user).first().is_up

    return JsonResponse(ret)
def comment(request):
    ret = {}
    print(request.POST)
    pid = request.POST.get("pid")
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    user_id = request.user.pk
    blog = request.user.blog
    if not pid:
        comment_obj = models.Comment.objects.create(user_id=user_id,article_id=article_id,content=content)
        models.Article.objects.update()
    else:
        comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content,parent_comment_id=pid)
        # models.Article.objects.update()

    # print(ret)
    ret["create_time"] = comment_obj.create_time
    ret["username"] = comment_obj.user.username
    ret["content"] = comment_obj.content
    print("comment==========")
    print(request.user)
    print(request.user.pk)



    return JsonResponse(ret)

# 评论树模式
def comment_tree(request,article_id):
    comment_list = list(models.Comment.objects.filter(article_id=article_id).values('pk','content','parent_comment_id'))
    return JsonResponse(comment_list,safe=False)


#ajax判断用户名是否存在
def check_user(request):

    username = request.GET.get("username")
    count = models.UserInfo.objects.filter(username=username).count()
    if count:
        list={"count":count}
        return JsonResponse(list)


def verification_code(request):
    #创建背景色
    bgColor = (random.randrange(50,100),random.randrange(50,100),0)
    #规定宽高
    width = 220
    height =35
    #创建画布
    image_obj = Image.new("RGB",(width,height),bgColor)
    #创建画笔
    draw = ImageDraw.Draw(image_obj)
    #创建文本内容
    text = '01234ABCDEFGHIJKLMN'
    rand_text =''
    font =ImageFont.truetype('static/font/consola.ttf',28)
    #构造字体颜色
    fontcolor = (255,random.randrange(50,255),random.randrange(0,255))
    #逐个绘制字符
    tmp_list = []
    for i in range(5):
        u = chr(random.randint(65, 90))  # 生成大写字母
        l = chr(random.randint(97, 122))  # 生成小写字母
        n = str(random.randint(0, 9))  # 生成数字，注意要转换成字符串类型

        tmp = random.choice([u, l, n])
        tmp_list.append(tmp)
        draw.text((20 + 40 * i, 0), tmp, fill=fontcolor, font=font)

    print("".join(tmp_list))
    print("生成的验证码".center(120, "="))
    request.session["valid_code"] = "".join(tmp_list)

    #加干扰线
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=fontcolor)

    # # 加干扰点
    for i in range(40):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=fontcolor)
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.arc((x, y, x+4, y+4), 0, 90, fill=fontcolor)

    # 将生成的图片保存在磁盘上
    # with open("s10.png", "wb") as f:
    #     img_obj.save(f, "png")
    # # 把刚才生成的图片返回给页面
    # with open("s10.png", "rb") as f:
    #     data = f.read()
    #不需要保存在磁盘上，直接在内存中加载就可以
    from io import BytesIO
    io_obj =BytesIO()
    #将生成的图片保存在io对象中
    image_obj.save(io_obj,'png')
    #从io对象里面取上一步保存的数据
    data = io_obj.getvalue()
    return HttpResponse(data)


# def register(request):
#     reform_obj = forms.RegForm()
#     print(reform_obj.fields)
#     if request.method == 'POST':
#         reform_obj = forms.RegForm(request.POST)
#         if reform_obj.is_valid():
#             del reform_obj.cleaned_data['re_password']
#             #去数据库创建一个新的用户
#             models.UserInfo.objects.create__user(**reform_obj.cleaned_data)
#             return HttpResponse('注册成功')
#
#     return render(request,'register.html',{'reform_obj':reform_obj})