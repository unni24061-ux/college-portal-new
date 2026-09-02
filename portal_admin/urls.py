from django.urls import path
from . import views

urlpatterns = [

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'faculty/approve/<int:id>/',
        views.approve_faculty,
        name='approve_faculty'
    ),

    path(
        'faculty/reject/<int:id>/',
        views.reject_faculty,
        name='reject_faculty'
    ),
]