from django import forms
from crm import models
from django.core.exceptions import ValidationError


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class RegForm(BaseForm):
    re_password = forms.CharField(label='确认密码',
                                  min_length=6,
                                  widget=forms.widgets.PasswordInput,
                                  error_messages={
                                      'min_length': '不能少于6位',
                                      'required': '不能为空'
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

    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')
        print(pwd, re_pwd)
        if pwd == re_pwd:
            print('两次密码一致，校验成功')
            return self.cleaned_data
        self.add_error('re_password', '两次密码不一致')
        raise ValidationError('两次密码不一致')


class CustomerForm(BaseForm):
    class Meta:
        model = models.Customer
        fields = '__all__'
        widgets = {
            'course': forms.widgets.SelectMultiple
        }


class ConsultRecordForm(BaseForm):
    class Meta:
        model = models.ConsultRecord
        exclude = ['delete_status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        customer_choice = [(i.id, i) for i in self.instance.consultant.customers.all()]
        customer_choice.insert(0, ('', '---'))

        # 限制客户是当前销售的私户
        self.fields['customer'].widget.choices = customer_choice
        # 限制跟进人是当前的用户（销售）
        self.fields['consultant'].widget.choices = [(self.instance.consultant.id, self.instance.consultant), ]


class EnrollmentForm(BaseForm):
    class Meta:
        model = models.Enrollment
        exclude = ['delete_status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #
        self.fields['customer'].widget.choices = [(self.instance.customer_id,self.instance.customer),]

        self.fields['enrolment_class'].widget.choices = [(i.id, i) for i in self.instance.customer.class_list.all()]
