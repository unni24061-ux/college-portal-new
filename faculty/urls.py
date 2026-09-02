"""
URL configuration for college_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from django.urls import path
from . import views

urlpatterns = [
    path('facultydash/',views.dashboard,name='facu_dash' ),
    path('f_profile/',views.f_profile,name='facu_profile'),
    path('edit_f_profile/',views.f_edit_profile,name='f_edit'),
    path('studentmanagment/',views.stud_manage,name='f_manage'),
    path('announcement/',views.announcement,name='announcement'),
    path('preview/<int:id>/',views.preview,name='preview'),
    path('preview/edit/<int:id>',views.edit_pro_f,name='profile_edit'),
    path('connect/',views.campus_connect,name='campus_connect'),
    path('notifications/',views.notification,name='f_notification'),
    




]
