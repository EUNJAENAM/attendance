from django import forms
from .models import User, Attendance

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['team_name', 'grade']
    
    def signup(self, request, user):
        user.team_name = self.cleaned_data['team_name']
        user.grade = self.cleaned_data['grade']        
        user.save()
        
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['absence_type', 
                  'start_date', 
                  'end_date',
                  'reason', 
                  'tot_time', 
                  'attachment1', 
                  'attachment2', 
                  'attachment3',
        ]
        widgets = {
            'absence_type': forms.RadioSelect,
                        'start_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',  # HTML5 datetime picker
                    'class': 'form-control',
                    'placeholder': '시작 날짜와 시간을 선택하세요',
                }
            ),
            'end_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',  # HTML5 datetime picker
                    'class': 'form-control',
                    'placeholder': '종료 날짜와 시간을 선택하세요',
                }
            ),
            'reason': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': '신청 사유를 입력하세요',
                    'rows': 3,
                }  
            )
        }
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'team_name',
            'grade',
            'profile_pic',
            'intro'            
        ]
        
        widgets = {
            'intro': forms.Textarea
        }