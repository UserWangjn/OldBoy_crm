from django import forms
from crm import models
from django.core.exceptions import ValidationError


class RegForm(forms.ModelForm):
    re_password = forms.CharField(label='确认密码',
                                  min_length=6,
                                  widget=forms.widgets.PasswordInput,
                                  error_messages={
                                      'min_length':'不能少于6位',
                                      'required':'不能为空'
                                  }
                                  )

    class Meta:
        model = models.UserProfile
        # fields = '__all__'        # 所有字段
        fields = ['username', 'password', 're_password', 'name', 'department']  # 指定字段
        widgets = {
            'password': forms.widgets.PasswordInput,
            'username': forms.widgets.EmailInput(attrs={'class': 'form-control'})
        }
        labels = {
            'username': '用户名',
            'password': '密码',
            'name': '姓名',
            'department': '部门',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')
        print(pwd,re_pwd)
        if pwd == re_pwd:
            print('两次密码一致，校验成功')
            return self.cleaned_data
        self.add_error('re_password','两次密码不一致')
        raise ValidationError('两次密码不一致')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = '__all__'
        widgets = {
            'course': forms.widgets.SelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class': 'form-control'})