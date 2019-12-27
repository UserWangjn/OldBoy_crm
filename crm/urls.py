from django.urls import path,re_path
from crm import views

urlpatterns = [
    # re_path('^customer_list/', views.customer_list,name='customer'),
    re_path('^customer_list/', views.CustomerList.as_view(),name='customer'),
    # re_path('^my_customer/', views.customer_list,name='my_customer'),
    re_path('^my_customer/', views.CustomerList.as_view(),name='my_customer'),
    re_path('^customer/add/', views.customer,name='add_customer'),
    re_path('^customer/edit/(\d+)', views.customer,name='edit_customer'),
]
