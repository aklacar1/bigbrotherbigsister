from django.contrib import admin
from datetime import datetime 
from django.contrib.auth import get_user_model

from .models import Department, VolunteerReport, Child, HangOutTheme

# class BaseAdmin(admin.ModelAdmin):
#     allowed_actions = ['ADD', 'CHANGE', 'NO_CHANGE', 'CHANGE_OWN', 'DELETE', 'NO_DELETE', 'DELETE_OWN', 'VIEW', 'VIEW_OWN']


class VolunteerReportAdmin(admin.ModelAdmin):
    list_display = ("description", "child", "text", "theme", "mood", "created_by", "department")
    search_fields = ['department__name', 'text', 'mood', 'created_by__username']

    list_filter = ('department', 'text', 'mood', 'created_by')

    def get_queryset(self, request):
        user = request.user
        # return Report.objects.filter(created_by_department=user.groups.all()[0])
        if Department.objects.all():
            department = Department.objects.filter(members=user)[0]
            return VolunteerReport.objects.filter(department=department)
        else:
            return VolunteerReport.objects.all()

admin.site.register(VolunteerReport, VolunteerReportAdmin)
            

class ChildAdmin(admin.ModelAdmin):
    list_display = ('jmbg', 'first_name', 'last_name', 'gender', 'department')
    search_fields = ('jmbg','first_name','last_name','gender')
    list_filter = ['gender']

    def get_queryset(self, request):
        user = request.user
        # return Report.objects.filter(created_by_department=user.groups.all()[0])
        if user.is_superuser:
            return Child.objects.all()            
        else:
            return Child.objects.filter(department=user.department)

admin.site.register(Child, ChildAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_members')
    
    def get_members(self, obj):
        User = get_user_model()
        users = User.objects.all()
        return ", ".join([str(i) for i in users])

    get_members.short_description = "Members"

admin.site.register(Department, DepartmentAdmin)

class HangOutThemeAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(HangOutTheme, HangOutThemeAdmin)
