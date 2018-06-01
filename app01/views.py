################################## 自定义验证码逻辑
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.shortcuts import HttpResponse
from string import ascii_letters, digits
import random
from random import randint

def generate_code():
    """生成六位数随机验证码"""
    code = "".join(random.sample(ascii_letters + digits, 6))
    return code

def get_random_color():
    return (randint(0, 255), randint(0, 255), randint(0, 255))

def get_valid_img(request):
    code = generate_code()
    request.session['valid_code'] = code
    # 1. 生成图片,颜色随机
    img = Image.new(mode="RGB", size=(213, 35), color=get_random_color())
    draw = ImageDraw.Draw(img, mode='RGB')  # 生成绘板对象
    # 2. 向图片写入内容
    font = ImageFont.truetype("static/fonts/kumo.ttf", 36)  # 字体样式必须引入, 字体大小
    # 保证每次生成不同的问题,且位数保证6位
    draw.text([60, 0], code, color=get_random_color(), font=font)  # 参数,:坐标, 文字, 颜色, 字体样式
    # 3. 保存到内存
    f = BytesIO()
    img.save(f, 'png')
    # 4. 读取图片
    data = f.getvalue()
    #  方式5, 验证码更新,必须是局部刷新,点击刷新
    return HttpResponse(data)


# ajax实现用户登录====================================
from django.contrib import auth
import json
from django.contrib.auth.hashers import make_password

def my_login(request):
    if request.method == "POST":
        errors = {}
        flag=True
        # 1,从session中获取本次请求生成的图片代码
        code = request.session.get("valid_code", '').upper()
        # 2. 获取用户提交的数据
        username = request.POST.get('username',"")
        pwd = request.POST.get('password',"")
        if not username:
            errors['password'] = '密码不能为空'
            flag=False
        if not username:
            errors['username'] = '用户名不能为空'
            flag=False
        valid_code = request.POST.get('valid_code',"")
        # 3. 判断验证码是否合格
        if valid_code.upper() != code:
            errors['valid_code']='验证码有误'
            flag=False

        # 4. 根据用户名和密码从数据库查询匹配的用户
        user = auth.authenticate(username=username, password=pwd)
        if user and flag==True:
            # 5. 找到用户,则创建或修改session信息, 修改为登录状态
            auth.login(request, user)
            return HttpResponse(json.dumps({'status': "success",'errors':{}}), content_type="application/json")
        errors['error_msg']='有户名或密码有误'

        return HttpResponse(json.dumps({'status': "fail", 'errors': errors,}),content_type="application/json")

    elif request.method == "GET":
        return render(request, 'login.html', {
        })


################################# 用户注册视图逻辑
from app01.forms import RegisterForm
from django.shortcuts import render
from app01.models import UserInfo

def register(request):
    if request.method == "GET":
        register_form = RegisterForm(request)
        return render(request, 'register.html', {
            'register_form': register_form,
        })

    elif request.method == 'POST':
        register_form = RegisterForm(request, request.POST,request.FILES)
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username', '')
            password = register_form.cleaned_data.get('password1', '')
            email = register_form.cleaned_data.get('email', '')
            file = request.FILES.get('avatar')
            UserInfo.objects.create_user(username=username, password=password, email=email, avatar=file)
            return HttpResponse('注册成功')

        errors = register_form.errors
        return render(request,'register.html',{'errors':errors,'register_form':register_form})


################################# 忘记密码和密码重置
from django.views import View
from app01.forms import ForgetPwdForms,ResetPwdForms
from django.shortcuts import HttpResponse,redirect
from app01.models import EmailValidCode
from django.contrib.auth.hashers import make_password

def generate_email_code():
    """生成六位数随机验证码"""
    code = "".join(random.sample(ascii_letters + digits, 32))
    return code


from django.core.mail import send_mail  # django自带的邮件发送模块
from pro_2.settings import EMAIL_FROM

def send_email(code,email):
    """发送邮件"""
    email_title = '博客忘记密码'
    email_body = '请点击下面的链接重置密码: http://127.0.0.1:8000/reset_pwd/{0}'.format(code)
    # 固定格式书写
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    if send_status:
        print('发送成功')

class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetPwdForms(request)
        return render(request, 'forget_pwd.html',{
            'forget_form':forget_form,
        })

    def post(self, request):
        forget_form = ForgetPwdForms(request,request.POST)
        if forget_form.is_valid():
            email = forget_form.cleaned_data['email']
            user = UserInfo.objects.filter(email=email)
            if user:
                # 生成邮箱验证码记录
                code = generate_email_code()
                email_code = EmailValidCode(code=code,email=email)
                email_code.save()
                # 发送邮件
                send_email(email=email,code=code)
                return HttpResponse('请前往邮箱查收!')

        errors = forget_form.errors
        return render(request, 'forget_pwd.html', {'errors': errors, 'forget_form': forget_form})


def reset_pwd(request, code):
    if request.method=='GET':
        pwd_form = ResetPwdForms(request)
        return render(request,'password_reset.html',{'pwd_form':pwd_form})

    if request.method=='POST':
        pwd_form = ResetPwdForms(request,request.POST)
        if pwd_form.is_valid():
            password = pwd_form.cleaned_data['password1']
            # 取用户信息
            email_code = EmailValidCode.objects.filter(code=code)
            if email_code:
                email=email_code[0].email
                user = UserInfo.objects.filter(email=email).first()
                user.password=make_password(password)
                user.save()
                return redirect('/login/')

        errors = pwd_form.errors
        return render(request, 'password_reset.html', {'pwd_form':pwd_form,'errors':errors})

def index(request):
    return render(request,'index.html')



################################# 分页制作
class Paginator(object):
    def __init__(self, current_page=0, total_count=0, show_page_num=9,per_page_count=0,obj_lst =[]):
        """
        :param current_page: 当前页码
        :param total_count: 数据总条数
        :param per_page_count:  每页显示的条数
        :param show_page_num:   显示页码数
        """
        self.current_page = int(current_page)
        self.per_page_count = int(per_page_count)
        self.show_page_num = int(show_page_num)
        self.total_count = int(total_count)
        self.obj_lst = obj_lst
        a, b = divmod(self.total_count, self.per_page_count)
        if b:
            total_pages = a + 1
        else:
            total_pages = a
        self.total_pages = total_pages  # 最大页数

    @property
    def start(self):
        """
        :return: 返回当前页的第一个数据的索引, 配合end方法使用,取出当前页的所有数据;
        """
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        """
        :return: 返回当前页的最后一套数据的数据的索引
        """
        return self.current_page * self.per_page_count

    @property
    def page_data(self):
        return self.obj_lst[self.start:self.end]

    @property
    def html_str(self):
        """ 生成分页文本"""
        # 1. 制作上一页和下一页---------------------------------------
        if self.current_page <= 1:
            prev_p = '<li class="disabled"><a href="#">上一页</a></li>'
        else:
            prev_p = '<li><a href="?page=%s">上一页</a></li>' % (self.current_page - 1)

        if self.current_page >= self.total_pages:
            next_p = '<li class="disabled"><a href="">下一页</a></li>'
        else:
            next_p = '<li><a href="?page=%s">下一页</a></li>' % (self.current_page + 1)

        # 2. 确保显示的页码数相同----------------------------------------

        if self.total_pages>self.show_page_num:
            half_show_page_num = int(self.show_page_num / 2)
            pager_start = self.current_page - half_show_page_num
            pager_end = self.current_page + half_show_page_num + 1
            # 判断最小页数不能小于1
            if self.current_page - self.show_page_num <= 1:
                pager_start = 1
                pager_end = pager_start + self.show_page_num + 1
            # 最大页数不能大于total_pages
            if self.current_page + self.show_page_num >= self.total_pages + 1:
                pager_end = self.total_pages
                pager_start = self.total_pages - self.show_page_num
        else:
            pager_start, pager_end=1,self.total_pages

        # 3. 制作当前页的页码显示------------------------------------
        page_list = []
        for i in range(pager_start, pager_end):
            if i == self.current_page:
                # 当前页高亮显示
                page_list.append('<li class="active"><a href="?page=%s">%s</a></li>' % (i, i))
            else:
                page_list.append('<li><a href="?page=%s">%s</a></li>' % (i, i))

        # 4. 将页码拼接成字符串
        page_str = '  '.join(page_list)
        # 5. 加上上一页和下一页
        page_str = prev_p + page_str + next_p
        return page_str


from app01.models import Book
from django.core.paginator import PageNotAnInteger,EmptyPage

def show_book(request):
    #########################　批量导入数据方法, 只连接一次数据库, 推荐方法
    # book_list = []
    # for i in range(100):
    #     book_list.append(Book(title="book%s" % i, price=30 + i))
    # Book.objects.bulk_create(book_list)
    # return HttpResponse('创建完成')

    ########################　分页显示数据
    # 1. 取出所有book对象
    book_list = Book.objects.all()
    # http://localhost:8802/?page=3
    page_num = request.GET.get('page')
    p = Paginator(per_page_count=10,total_count=book_list.count(),
                  current_page=page_num,show_page_num=13,obj_lst=book_list)

    page_data = p.page_data
    pager_str = p.html_str
    return render(request, "book.html", locals())



from django.utils import safestring
from app01.models import Book

def pager(request):
    """解决分页"""
    # 1. 取出所有对象
    books = Book.objects.all()
    # 2. 通过url的传输的参数拿到当前页码
    current_page = int(request.GET.get('page', 1))
    # 3. 每页显示10条
    per_page_count = 10
    # 4. 推算出当前页码数,每页显示数量和最终筛选条件的关系
    start = (current_page - 1) * per_page_count
    end = current_page * per_page_count
    '''
    例如:
    	页码		取值范围
    	1		[0:10]
    	2		[10:20]
    	3		[20:30]
    	n		[(n-1*10):n*10]
    '''

    # 5. 筛选出当前页数据
    books = books[start: end]
    page_list = []

    # 6. 计算总的页数
    # 例如,当前每页10条,总数据为301条,则显示为31页
    total_count = Book.objects.all().count()
    a, b = divmod(total_count, per_page_count)

    '''
    301/10=30+1 # 31页
    300/10=30   # 30页
    '''

    if b:
        total_pages = a + 2  # a+1
    else:
        total_pages = a + 1  # a

    # 7. 配置上一页和下一页,
    if current_page == 1:
        prev_p = '<li class="disabled"><a href="#">上一页</a></li>'
    else:
        prev_p = '<li><a href="?page=%s">上一页</a></li>' \
                 % (current_page - 1)

    if current_page + 1 == total_pages:
        next_p = '<li class="disabled"><a href="">下一页</a></li>'
    else:
        next_p = '<li><a href="?page=%s">下一页</a></li>' \
                 % (current_page + 1)

    # 8. 保证显示的页码个数相同[1 2 3 4 5]
    show_page_num = 10
    half_show_page_num = int(show_page_num / 2)  # 2

    pager_start = current_page - half_show_page_num
    pager_end = current_page + half_show_page_num + 1

    # 9. 判断最小页数不能小于1
    if current_page - show_page_num <= 1:
        pager_start = 1
        pager_end = pager_start + show_page_num + 1

    # 10, 最大页数不能大于total_pages
    if current_page + show_page_num >= total_pages + 1:
        pager_end = total_pages
        pager_start = total_pages - show_page_num

    for i in range(pager_start, pager_end):
        if i == current_page:
            page_list.append('<li class="active"><a href="?page=%s">%s</a></li>' % (i, i))
        else:
            page_list.append('<li><a href="?page=%s">%s</a></li>' % (i, i))

    page_str = '  '.join(page_list)
    page_str = prev_p + page_str + next_p
    page_str = safestring.mark_safe(page_str)

    return render(request, 'pager.html', {
        'books': books,
        'page_str': page_str,
    })