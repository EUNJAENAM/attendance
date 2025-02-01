from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Attendance

# Register your models here.

# admin.site.register(User, UserAdmin)
# fieldsets = UserAdmin.fieldsets + (
#     ("Custom fields", {  # 새 섹션의 제목
#         "fields": ('team_name', 'grade', 'profile_pic',' intro'),  # user 파일에 추가할 필드
#     }),
# )

# UserAdmin 커스터마이징
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 기존 UserAdmin의 필드셋에 Custom Fields 추가
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {  # 섹션 제목
            "fields": ('team_name', 'grade', 'profile_pic', 'intro'),  # 추가할 필드
        }),
    )

    # 관리자 페이지의 사용자 목록에 표시할 필드
    list_display = UserAdmin.list_display + ('team_name', 'grade','profile_pic', 'intro')


admin.site.register(Attendance)
