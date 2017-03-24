"""myapp2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from login import views
from django.contrib.auth.views import login

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index_view, name='index'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^logout_success/$', views.user_logout_success, name='logout_success'),
    url(r'^login/success/$', views.user_login_success, name='success'),
    url(r'^register/$', views.register_view, name='register'),
    url(r'^register/success/$', views.register_success, name='register_success'),
    url(r'^usersites/$', views.user_view, name='usersite'),
    url(r'^usersites/student/$', views.student_view, name='student'),
    url(r'^usersites/teacher/$', views.teacher_view, name='teacher'),
    url(r'^home/$', views.homepage_view, name='homepage'),
    url(r'^course/$', views.course_view, name='course'),
]
