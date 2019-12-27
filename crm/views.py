from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from crm import forms, models
from utils.pagination import Pagination
from django.urls import reverse
from django.views import View
from django.db.models import Q
import copy


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
    return render(request, 'crm/customer_list.html', {
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
        page = Pagination(request, all_customer.count(), query_params, per_num=2)
        next_url = request.get_full_path()
        return render(request, 'crm/customer_list.html', {
            "all_customer": all_customer[page.start:page.end],
            'pagination': page.show_li,
            'next_url': next_url}
                      )

    def post(self, request):
        # print(request.POST)   # <QueryDict: {'csrfmiddlewaretoken': ['KOIBZh8aVJ7xQM7ZxwgZfK4Wd3atAa1BdbxJJyx4x3g4W7eJfS5MkppIvuwGRFMC'], 'action': ['multi_to_pri'], 'id': ['2', '3', '6']}>
        action = request.POST.get('action')
        if not hasattr(self, action):
            return HttpResponse('不存在的操作')
        ret = getattr(self, action)()

        return redirect(reverse('customer'))

    def multi_to_pri(self):
        select_ids = self.request.POST.getlist('id')
        models.Customer.objects.filter(id__in=select_ids).update(consultant=self.request.user)

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


# 新增和编辑客户
def customer(request, edit_id=None):
    url = request.get_full_path()
    edit_obj = models.Customer.objects.filter(id=edit_id).first()
    form_obj = forms.CustomerForm(instance=edit_obj)
    if request.method == 'POST':
        form_obj = forms.CustomerForm(request.POST, instance=edit_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('customer'))
    return render(request, 'crm/customer.html', {'form_obj': form_obj, 'edit_obj': edit_obj})
