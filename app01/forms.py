from django import forms
from django.forms import widgets
from django.forms import ValidationError


class RegisterForm(forms.Form):
    # 可以在error_messages中自定义错误信息
    username = forms.CharField(min_length=2, error_messages={'required':'用户名不能为空','min_length':'至少为4位'},
                               widget=widgets.TextInput(attrs={"placeholder": "用户名"}))
    password1 = forms.CharField(min_length=4, error_messages={'required':'密码不能为空','min_length':'至少为4位'},
                                widget=widgets.PasswordInput(attrs={"placeholder": "密码1"}))
    password2 = forms.CharField(min_length=4, error_messages={'required':'密码不能为空','min_length':'至少为4位'},
                                widget=widgets.PasswordInput(attrs={"placeholder": "密码2"}))
    email = forms.EmailField(max_length=50, error_messages={'required':'邮箱不能为空格','min_length':'至少为4位'},
                             widget=widgets.EmailInput(attrs={"placeholder": "邮箱"}))
    valid_code = forms.CharField(min_length=6, error_messages={'required':'验证码不能为空','min_length':'至少为6位',
                                                               },
                                 max_length=6, widget=widgets.TextInput(attrs={"placeholder": "验证码"}))

    def __init__(self, request, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.request = request

    def clean_password1(self):
        '''自定义密码检测'''
        if self.cleaned_data['password1'].isalpha() or self.cleaned_data['password1'].isdigit():
            raise ValidationError('密码不能全为数字或者字母')
        else:
            return self.cleaned_data['password1']

    def clean_password2(self):
        '''自定义密码检测'''
        if len(self.cleaned_data['password2']) < 6:
            raise ValidationError('密码长度小于六位')
        elif self.cleaned_data['password2'].isalpha() or self.cleaned_data['password2'].isdigit():
            raise ValidationError('密码不能全为数字或者字母')
        else:
            return self.cleaned_data['password2']

    def clean_valid_code(self):
        '''检测验证码是否匹配'''
        if self.cleaned_data["valid_code"].upper() == self.request.session["valid_code"].upper():
            return self.cleaned_data["valid_code"]
        else:
            print('验证码错误')
            raise ValidationError("验证码错误！")

    def clean(self):
        '''密码一致性检测'''
        if self.cleaned_data.get('password1','') == self.cleaned_data.get('password2',''):
            return self.cleaned_data
        else:
            raise ValidationError("密码不一致")



from django import forms
from app01.models import UserInfo

class ForgetPwdForms(forms.Form):
    email = forms.EmailField(max_length=30,error_messages={'required': '验证码不能为空'})
    valid_code = forms.CharField(min_length=6, error_messages={'required': '验证码不能为空', 'min_length': '至少为6位'},
                                 max_length=6, widget=widgets.TextInput(attrs={"placeholder": "验证码"}))

    def __init__(self, request, *args, **kwargs):
        super(ForgetPwdForms, self).__init__(*args, **kwargs)
        self.request = request

    def clean_email(self):
        email = self.cleaned_data['email']
        user = UserInfo.objects.filter(email=email)
        if user:
            return email
        raise ValidationError('该邮箱没有注册')

    def clean_valid_code(self):
        '''检测验证码是否匹配'''
        if self.cleaned_data["valid_code"].upper() == self.request.session["valid_code"].upper():
            return self.cleaned_data["valid_code"]
        else:
            print('验证码错误')
            raise ValidationError("验证码错误！")


class ResetPwdForms(forms.Form):
    password1 = forms.CharField(min_length=6, max_length=20,
                                error_messages={'required':'密码不能为空','min_length':'至少为6位','max_length':'最多为20位'})
    password2 = forms.CharField(min_length=6, max_length=20,
                                error_messages={'required':'密码不能为空','min_length':'至少为6位','max_length':'最多为20位'})

    def __init__(self, request, *args, **kwargs):
        super(ResetPwdForms, self).__init__(*args, **kwargs)
        self.request = request

    def clean_password2(self):
        '''自定义密码检测'''
        # if len(self.cleaned_data['password2']) < 6:
        #     raise ValidationError('密码长度小于六位')
        if self.cleaned_data['password2'].isalpha() or self.cleaned_data['password2'].isdigit():
            raise ValidationError('密码不能全为数字或者字母')
        else:
            return self.cleaned_data['password2']

    def clean_password1(self):
        '''自定义密码检测'''
        # if len(self.cleaned_data['password1']) < 6:
        #     raise ValidationError('密码长度小于六位')
        if self.cleaned_data['password1'].isalpha() or self.cleaned_data['password1'].isdigit():
            raise ValidationError('密码不能全为数字或者字母')
        else:
            return self.cleaned_data['password1']

    def clean(self):
        '''密码一致性检测'''
        if self.cleaned_data.get('password1') == self.cleaned_data.get('password2'):
            return self.cleaned_data
        else:
            raise ValidationError("密码不一致")



