"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.contrib import admin

from core import views as core_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', core_views.home, name='home'),
    url(r'^viewchild/$', core_views.viewchild, name='viewchild'),

    url(r'^auth_select/$', core_views.auth_member_select, name='auth_member_select'),
    url(r'^auth_select/submit$', core_views.auth_member_submit, name='auth_member_submit'),

    url(r'^deauth_select/$', core_views.deauth_member_select, name='deauth_member_select'),
    url(r'^deauth_select/submit$', core_views.deauth_member_submit, name='deauth_member_submit'),


    url(r'^assign_select/$', core_views.assignmed_select, name='assignmed_select'),
    url(r'^assign_select/submit$', core_views.assignmed_submit, name='assignmed_submit'),

    url(r'^add$', core_views.addImmunizations, name='addImmun'),
    url(r'^add/submit$', core_views.addImmunizations_submit, name='addImmun_submit'),

    url(r'^success/$', core_views.success, name='success'),
    url(r'^failure/$', core_views.failure, name='failure'),
    url(r'^newchild/$', core_views.newchild, name='newchild'),
    url(r'^update/$', core_views.update, name='update'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^signup/$', core_views.signup, name='signup'),
]
