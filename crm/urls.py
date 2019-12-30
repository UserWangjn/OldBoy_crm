from django.urls import re_path
from crm.views import consultant, teacher

urlpatterns = [
    # 共有客户
    # re_path('^customer_list/', views.customer_list,name='customer'),
    re_path('^customer_list/', consultant.CustomerList.as_view(), name='customer'),
    # 私有客户
    # re_path('^my_customer/', views.customer_list,name='my_customer'),
    re_path('^my_customer/', consultant.CustomerList.as_view(), name='my_customer'),
    # 新增客户
    re_path('^customer/add/', consultant.customer, name='add_customer'),
    # 编辑客户
    re_path('^customer/edit/(\d+)/', consultant.customer, name='edit_customer'),
    # 展示跟进记录
    re_path('^consult_record_list/(\d+)/', consultant.ConsultRecord.as_view(), name='consult_record'),
    # 新增跟进记录
    re_path('^consult_record/add/', consultant.consult_record, name='add_consult_record'),
    # 编辑跟进记录
    re_path('^consult_record/edit/(\d+)/', consultant.consult_record, name='edit_consult_record'),
    # 展示报名记录
    re_path('^enrollment_list/(?P<customer_id>\d+)', consultant.EnrollmentList.as_view(), name='enrollment'),
    # 添加报名表
    re_path('^enrollment/add/(?P<customer_id>\d+)', consultant.enrollment, name='add_enrollment'),
    # 编辑报名表
    re_path('^enrollment/edit/(?P<edit_id>\d+)', consultant.enrollment, name='edit_enrollment'),
    # 展示班级列表
    re_path('^class_list/', teacher.ClassList.as_view(), name='class_list'),
    # 新增班级列表
    re_path('^class/add/', teacher.classes, name='add_class'),
    # 编辑班级列表
    re_path('^class/edit/(\d+)', teacher.classes, name='edit_class'),
    # 展示某个班级的课程记录
    re_path('^course_list/(\d+)', teacher.CourseList.as_view(), name='course_list'),
    # 新增课程列表
    re_path('^course/add/(?P<class_id>\d+)', teacher.course, name='add_course'),
    # 编辑课程列表
    re_path('^course/edit/(?P<edit_id>\d+)', teacher.course, name='edit_course'),
]
