from django.urls import path, re_path
from crm import views

urlpatterns = [
    # 共有客户
    # re_path('^customer_list/', views.customer_list,name='customer'),
    re_path('^customer_list/', views.CustomerList.as_view(), name='customer'),
    # 私有客户
    # re_path('^my_customer/', views.customer_list,name='my_customer'),
    re_path('^my_customer/', views.CustomerList.as_view(), name='my_customer'),
    # 新增客户
    re_path('^customer/add/', views.customer, name='add_customer'),
    # 编辑客户
    re_path('^customer/edit/(\d+)/', views.customer, name='edit_customer'),
    # 展示跟进记录
    re_path('^consult_record_list/(\d+)/', views.ConsultRecord.as_view(), name='consult_record'),
    # 新增跟进记录
    re_path('^consult_record/add/', views.consult_record, name='add_consult_record'),
    # 编辑跟进记录
    re_path('^consult_record/edit/(\d+)/', views.consult_record, name='edit_consult_record'),
    # 展示报名记录
    re_path('^enrollment_list/(?P<customer_id>\d+)', views.EnrollmentList.as_view(), name='enrollment'),
    # 添加报名表
    re_path('^enrollment/add/(?P<customer_id>\d+)', views.enrollment, name='add_enrollment'),
# 编辑报名表
    re_path('^enrollment/edit/(?P<edit_id>\d+)', views.enrollment, name='edit_enrollment'),
]
