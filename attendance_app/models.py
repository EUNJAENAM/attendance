from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import validate_no_special_characters
from django.utils.timezone import now
from datetime import timedelta

# Create your models here.

class User(AbstractUser):
    
    team_name = models.CharField(
        max_length=15, 
        null=True,
        validators=[validate_no_special_characters]
    )
    
    grade = models.CharField(
        max_length=15, 
        null=True,
        validators=[validate_no_special_characters]    
    )
    
    profile_pic = models.ImageField(default='default_profile_pic.jpg',upload_to='profile_pics')
    
    intro = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.email

class Attendance(models.Model):
    TYPE_CHOICES = [
        ('ABSENCE', '결근'),
        ('ANNUAL_LEAVE', '연차'),
        ('LATE', '지각'),
        ('EARLY_LEAVE', '조퇴'),
        ('BUSINESS_TRIP', '출장'),
    ]
    absence_type = models.CharField(max_length=20, 
                                    choices=TYPE_CHOICES, 
                                    verbose_name="근태 유형", 
                                    default=None)
    start_date = models.DateTimeField(verbose_name="시작 시점", default=now)
    end_date = models.DateTimeField(verbose_name="종료 시점", null=True, blank=True)
    reason = models.TextField(verbose_name="신청 사유", null=True, blank=True) 
    tot_time = models.FloatField(default=0.0)
    attachment1 = models.FileField(
        upload_to="attendance_pics",
        verbose_name = "첨부파일",
        null = True,
        blank = True
    )
    attachment2 = models.FileField(
        upload_to="attendance_pics",
        verbose_name = "첨부파일",
        null = True,
        blank = True
    )
    attachment3 = models.FileField(
        upload_to="attendance_pics",
        verbose_name = "첨부파일",
        null = True,
        blank = True
    )
    
        # 팀장 승인자
    team_leader_approver = models.CharField(
        max_length=50, 
        verbose_name="팀장 승인자",
        null=True,
        blank=True
    )

        # 팀장 승인 일자
    team_leader_approval_date = models.DateTimeField(
        verbose_name="팀장 승인일자",
        null=True,
        blank=True
    )

    # 최종 승인자
    final_approver = models.CharField(
        max_length=50, 
        verbose_name="최종 승인자",
        null=True,
        blank=True
    )

    # 최종 승인 일자
    final_approval_date = models.DateTimeField(
        verbose_name="최종 승인일자",
        null=True,
        blank=True
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_requests',
        verbose_name='신청자'
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_absence_type_display()} ({self.start_date} ~ {self.end_date if self.end_date else '미지정'})"

    class Meta:
        verbose_name = "근태 신청서"
        verbose_name_plural = "근태 신청서"
        ordering = ['-start_date']
        
    # def save(self, *args, **kwargs):
    #     if self.start_date and self.end_date:
    #         sutation = (self.end_date - self.start_date).total_seconds()
    #         self.tot_time = sutation / 3600  #시간 단위로 계산
    #     super().save(*args, **kwargs)
    
        # 근무 시간 관련 설정
    work_start_hour = 9
    work_start_minute = 0  # 근무 시작 시간 (09:00)
    work_end_hour = 18
    work_end_minute = 0  # 근무 종료 시간 (18:00)
    lunch_start_hour = 12
    lunch_start_minute = 0  # 점심 시작 시간 (12:00)
    lunch_end_hour = 13
    lunch_end_minute = 0  # 점심 종료 시간 (13:00)

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            total_hours = 0
            current_date = self.start_date

            while current_date.date() <= self.end_date.date():
                # 당일 시작 시간 계산
                start_of_day = max(
                    current_date,
                    self.start_date if current_date.date() == self.start_date.date() else current_date.replace(hour=self.work_start_hour, minute=self.work_start_minute, second=0)
                )

                # 당일 종료 시간 계산
                end_of_day = min(
                    self.end_date if current_date.date() == self.end_date.date() else current_date.replace(hour=self.work_end_hour, minute=self.work_end_minute, second=0),
                    self.end_date
                )

                # 점심시간 계산
                lunch_start = current_date.replace(hour=self.lunch_start_hour, minute=self.lunch_start_minute, second=0)
                lunch_end = current_date.replace(hour=self.lunch_end_hour, minute=self.lunch_end_minute, second=0)

                # 점심시간 제외 계산
                if start_of_day < lunch_start < end_of_day:  # 근무 시간 내에 점심시간이 포함될 경우
                    effective_end = min(lunch_start, end_of_day)
                    effective_start = max(start_of_day, lunch_end)
                    daily_hours = (effective_end - start_of_day).total_seconds() / 3600 + (end_of_day - effective_start).total_seconds() / 3600
                else:  # 점심시간이 근무시간과 겹치지 않을 경우
                    daily_hours = (end_of_day - start_of_day).total_seconds() / 3600

                # 하루 8시간까지만 인정
                total_hours += min(daily_hours, 8)

                # 다음 날로 이동
                current_date = (current_date + timedelta(days=1)).replace(hour=0, minute=0, second=0)

            self.tot_time = total_hours

        super().save(*args, **kwargs)