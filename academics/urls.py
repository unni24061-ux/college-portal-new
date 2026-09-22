from django.urls import path

from . import views

urlpatterns = [
    path('attendance/start/', views.start_session, name='attendance_start'),
    path('attendance/refresh/', views.refresh_token, name='attendance_refresh'),
    path('attendance/end/<int:pk>/', views.end_session, name='attendance_end'),
    path('attendance/checkin/', views.check_in, name='attendance_checkin'),
]