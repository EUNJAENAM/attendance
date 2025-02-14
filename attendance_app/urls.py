from django.urls import path
from .views import attendance_data
from . import views

app_name = 'attendance_app'

urlpatterns = [
     # 근태신청서 urls
    path("", views.IndexView.as_view(), name='index'),
    path("detailviews/<int:attendance_id>/", 
         views.AttendanceDetailView.as_view(), 
         name='attendance-detail',
    ),
    path("attendance/new/", 
         views.AttendanceCreateView.as_view(), 
         name='attendance-create',
    ),
    path("attendance/<int:attendance_id>/edit/", 
         views.AttendanceUpdateView.as_view(), 
         name='attendance-update',
    ),    
    path("attendance/<int:attendance_id>/delete/", 
         views.AttendanceDeleteView.as_view(), 
         name='attendance-delete',
    ),   
    path('attendance/<int:attendance_id>/approve/', views.ApproveAttendance, name='approve-attendance'),
             
    ## 개인정보  urls
    path('users/<int:user_id>/',views.ProfileView.as_view(), name='profile'),
    path('users/<int:user_id>/attendance',views.UserAttendanceList.as_view(), name='user-attendance-list'),
    path('set-profile/', views.ProfileSetView.as_view(), name='profile-set'),
    path('edit-profile/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('attendance-data/', attendance_data, name='attendance_data'),    
]