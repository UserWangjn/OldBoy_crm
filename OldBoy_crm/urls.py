"""OldBoy_crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path,include
from crm.views import consultant

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('^login/', consultant.login),   # 用户名：admin@qq.com  密码：admin1234
    re_path('^reg/', consultant.reg),
    re_path('^crm/', include('crm.urls')),
]
