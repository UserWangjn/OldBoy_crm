from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from crm import forms, models
from utils.pagination import Pagination
from django.urls import reverse
from django.views import View
from django.db.models import Q
import copy
from django.http import QueryDict
from django.utils.safestring import mark_safe
from django.db import transaction


def login(request):
    err_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        obj = auth.authenticate(request, username=username, password=password)
        if obj:
            auth.login(request, obj)
            return redirect(reverse('customer'))
        err_msg = '您的用户名或密码不正确'
    return render(request, 'login.html', {'err_msg': err_msg})


def reg(request):
    form_obj = forms.RegForm()
    if request.method == 'POST':
        form_obj = forms.RegForm(request.POST)
        # print('form_obj.errors',form_obj.errors)    # 如果该方法form_obj.is_valid()进不去，
        # 一直为false,可以用这个errors方法看哪个字段报错
        if form_obj.is_valid():
            # 创建新用户
            # 方式一
            # form_obj.cleaned_data.pop('re_password')
            # models.UserProfile.objects.create_user(**form_obj.cleaned_data)
            obj = form_obj.save()
            obj.set_password(obj.password)
            obj.save()
            return redirect('/login/')

    return render(request, 'reg.html', {'form_obj': form_obj})


# 公户客户
def customer_list(request):
    # 查询公户（没有销售顾问）
    if request.path_info == reverse('customer'):
        all_customer = models.Customer.objects.filter(consultant__isnull=True)
    # 查询私户
    else:
        all_customer = models.Customer.objects.filter(consultant=request.user)
    page = Pagination(request, all_customer.count())
    return render(request, 'crm/consultant/customer_list.html', {
        "all_customer": all_customer[page.start:page.end],
        'pagination': page.show_li})


class CustomerList(View):

    def get(self, request):
        # print(request.GET)
        q = self.get_search_contion(['qq', 'name', 'last_consult_date'])
        # 查询公户（没有销售顾问）
        if request.path_info == reverse('customer'):
            all_customer = models.Customer.objects.filter(q,
                                                          consultant__isnull=True)
        # 查询私户
        else:
            all_customer = models.Customer.objects.filter(q,
                                                          consultant=request.user)
        query_params = copy.deepcopy(request.GET)
        # print('query_params:',query_params)
        page = Pagination(request, all_customer.count(), query_params)
        add_btn, next_url = self.get_add_btn()
        # print('add_btn:', add_btn)
        # print('next_url:', next_url)
        return render(request, 'crm/consultant/customer_list.html', {
            "all_customer": all_customer[page.start:page.end],
            'pagination': page.show_li,
            'add_btn': add_btn,
            'next_url': next_url
        })

    def post(self, request):
        # print(request.POST)   # <QueryDict: {'csrfmiddlewaretoken': ['KOIBZh8aVJ7xQM7ZxwgZfK4Wd3atAa1BdbxJJyx4x3g4W7eJfS5MkppIvuwGRFMC'], 'action': ['multi_to_pri'], 'id': ['2', '3', '6']}>
        action = request.POST.get('action')
        if not hasattr(self, action):
            return HttpResponse('不存在的操作')
        ret = getattr(self, action)()
        if ret:
            return ret
        # return redirect(reverse('customer'))
        return self.get(request)

    # 公户变私户
    def multi_to_pri(self):
        select_ids = self.request.POST.getlist('id')
        # 申请数量
        apply_num = len(select_ids)
        with transaction.atomic():
            # transaction.atomic()事务，原子性操作。select_for_update()行级锁，防止多个人抢一个客户出现问题
            obj_list = models.Customer.objects.filter(id__in=select_ids, consultant__isnull=True).select_for_update()
            if len(obj_list) == apply_num:
                obj_list.update(consultant=self.request.user)
            else:
                return HttpResponse('您提交的客户中有已经被别人抢走了')

    # 私户变公户
    def multi_to_pub(self):
        select_ids = self.request.POST.getlist('id')
        models.Customer.objects.filter(id__in=select_ids).update(consultant=None)

    def get_search_contion(self, query_list):
        query = self.request.GET.get('query', '')

        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))

        return q

    def get_add_btn(self):
        next = self.request.get_full_path()
        qd = QueryDict()
        qd._mutable = True
        qd['next'] = next
        next_url = qd.urlencode()
        # print('qd:',qd.urlencode())  # qd: next=%2Fcrm%2Fcustomer_list%2F%3Fquery%3D11%26page%3D3
        # print('qd:',qd)     # qd: <QueryDict: {'next': ['/crm/customer_list/?query=11&page=3']}>
        add_btn = '<a href="{}?{}" class="btn btn-primary btn-sm">新增</a>'.format(reverse('add_customer'), next_url)

        return mark_safe(add_btn), next_url


# 新增和编辑客户
def customer(request, edit_id=None):
    edit_obj = models.Customer.objects.filter(id=edit_id).first()
    form_obj = forms.CustomerForm(instance=edit_obj)
    if request.method == 'POST':
        form_obj = forms.CustomerForm(request.POST, instance=edit_obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('customer'))
    return render(request, 'crm/consultant/customer.html', {'form_obj': form_obj, 'edit_obj': edit_obj})


# 展示跟进记录
class ConsultRecord(View):

    def get(self, request, customer_id):
        if customer_id == '0':
            all_consult_record = models.ConsultRecord.objects.filter(delete_status=False)
        else:
            all_consult_record = models.ConsultRecord.objects.filter(customer_id=customer_id, delete_status=False)
        query_params = copy.deepcopy(request.GET)
        page = Pagination(request, all_consult_record.count(), query_params, per_num=2)
        return render(request, 'crm/consultant/consult_record_list.html', {
            "all_consult_record": all_consult_record[page.start:page.end],
            'pagination': page.show_li,
        })


# 新增和编辑跟进记录
def consult_record(request, edit_id=None):
    obj = models.ConsultRecord.objects.filter(id=edit_id).first() or models.ConsultRecord(consultant=request.user)
    form_obj = forms.ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = forms.ConsultRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record', args=(0,)))
    return render(request, 'crm/consultant/consult_record.html', {'form_obj': form_obj})


# 展示报名记录
class EnrollmentList(View):
    def get(self, request, customer_id):
        if customer_id == '0':
            all_enrollment = models.Enrollment.objects.filter(delete_status=False, customer__consultant=request.user)
        else:
            all_enrollment = models.Enrollment.objects.filter(customer_id=customer_id, delete_status=False)
        next_url = self.get_next_url()
        return render(request, 'crm/consultant/enrollment_list.html', {'all_enrollment': all_enrollment,
                                                            'next_url': next_url})

    def get_next_url(self):
        next = self.request.get_full_path()
        qd = QueryDict()
        qd._mutable = True
        qd['next'] = next
        next_url = qd.urlencode()

        return next_url


# 新增和编辑报名表
def enrollment(request, customer_id=None, edit_id=None):
    obj = models.Enrollment.objects.filter(id=edit_id).first() or models.Enrollment(customer_id=customer_id)
    form_obj = forms.EnrollmentForm(instance=obj)

    if request.method == 'POST':
        form_obj = forms.EnrollmentForm(request.POST, instance=obj)
        if form_obj.is_valid():
            enrollment_obj = form_obj.save()
            enrollment_obj.customer.status = 'signed'
            enrollment_obj.customer.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('my_customer'))
    return render(request, 'crm/consultant/enrollment.html', {'form_obj': form_obj,
                                                   'edit_id': edit_id})
