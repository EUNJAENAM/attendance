from django.utils import timezone 
from django.shortcuts import render, get_object_or_404, redirect
from allauth.account.views import PasswordChangeView
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView,
    DeleteView,
)
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from allauth.account.models import EmailAddress
from attendance_app.models import Attendance
from attendance_app.forms import AttendanceForm, ProfileForm
from attendance_app.functions import confirmation_required_redirect
from django.contrib.auth.decorators import login_required
from .models import User

# import logging
# from django.http import JsonResponse

# Create your views here.

# def index(request):
#     return render(request, 'attendance_app/index.html')

class IndexView(ListView):
    model = Attendance
    template_name = 'attendance_app/index.html'
    context_object_name = 'attendance'
    paginate_by = 3
    ordering = ['-id']
    
class AttendanceDetailView(DetailView):
    model = Attendance
    template_name = 'attendance_app/attendance_detail.html'
    pk_url_kwarg = 'attendance_id'      #키값 전달    
    
class AttendanceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance_app/attendance_form.html'    
    
    redirect_unauthenticated_users = True                  #이메일 인증에 관한 처리
    raise_exception = confirmation_required_redirect    
    
    def form_valid(self, form):                  #유효성 검증 후 저장
        form.instance.user = self.request.user   # 폼에 user를 추가해 주고
        return super().form_valid(form)          # author 값이 폼에 전달됨
    
    def get_success_url(self):
        return reverse("attendance_app:attendance-detail", kwargs={'attendance_id': self.object.id}) 
    
    def test_func(self, user):
        return EmailAddress.objects.filter(user=user, verified=True).exists()
            
class AttendanceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance_app/attendance_form.html'
    pk_url_kwarg = 'attendance_id'
    
    raise_exception = True                       # 본인작성글 검증, 주소창에 직접주소 등록의 경우도 처리
    redirect_unauthenticated_users = False
    
    def get_success_url(self):
        return reverse("attendance_app:attendance-detail", kwargs={'attendance_id': self.object.id})      

    def test_func(self, user):
        gab = self.get_object()
        return gab.user == user    

class AttendanceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Attendance
    template_name = 'attendance_app/attendance_confirm_delete.html'
    pk_url_kwarg = 'attendance_id'
    
    raise_exception = True                       # 본인작성글 검증, 주소창에 직접주소 등록의 경우도 처리
    redirect_unauthenticated_users = False    
    
    def get_success_url(self):
        return reverse("attendance_app:index")   
    
    def test_func(self, user):
        gab = self.get_object()
        return gab.user == user      
    
class ProfileView(DetailView):
    model=User
    template_name = 'attendance_app/profile.html'
    pk_url_kwarg='user_id'    
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        context['user_attendance']=Attendance.objects.filter(user=user_id).order_by("-id")[:4]
        return context
    
# class UserAttendanceList(ListView):
#     model = Attendance
#     template_name = 'attendance_app/user_attendance_list.html'
#     context_object_name = 'user_attendance'
#     paginate_by = 4
    
#     def get_queryset(self):
#         user_id = self.kwargs.get('user_id')
#         return Attendance.objects.filter(user_id=user_id).order_by('id')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['profile_user'] = get_object_or_404(User, id=self.kwargs.get('user_id'))
#         return context
    
class UserAttendanceList(ListView):
    model = Attendance
    template_name = 'attendance_app/user_attendance_list.html'
    context_object_name = 'user_attendance'
    paginate_by = 3
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        current_user = get_object_or_404(User, id=user_id)     # 현재 사용자 정보 가져옴
        
        if current_user.grade == "master":  # 직책이 "master"인 경우
            return Attendance.objects.all().order_by('id')  # 전체 데이터를 반환
        else:
            # 팀명이 같은 사용자들의 데이터 필터링
            return Attendance.objects.filter(user__team_name=current_user.team_name).order_by('id')
      
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = get_object_or_404(User, id=self.kwargs.get('user_id'))
        return context
    
class ProfileSetView(LoginRequiredMixin, UpdateView):      # 로그인된 사용자인지 검증 LoginRequiredMixin
    model = Attendance
    form_class=ProfileForm
    template_name = 'attendance_app/profile_set_form.html'
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse('attendance_app:index')
    

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Attendance
    form_class=ProfileForm
    template_name = 'attendance_app/profile_update_form.html'
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse('attendance_app:profile', kwargs=({'user_id':self.request.user.id}))
    
    
@login_required
def ApproveAttendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id)
    profile_user = request.user
    
    # 팀장 승인자 저장
    if profile_user.grade == "팀장":  # 팀장인지 확인
        attendance.team_leader_approver = profile_user.username
        attendance.team_leader_approval_date = timezone.now()
        attendance.save()

    # 인사담당 승인자 저장
    if profile_user.grade == "master":  # 팀장인지 확인
        attendance.final_approver = profile_user.username
        attendance.final_approval_date = timezone.now()
        attendance.save()
        
    return redirect('attendance_app:user-attendance-list', user_id=profile_user.id)
        
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    
    def get_success_url(self):
        return reverse('attendance_app:profile', kwargs=({'user_id':self.request.user.id}))