import csv
from datetime import datetime 
import uuid
from typing import Dict, List

from adminsortable.admin import SortableAdmin, SortableStackedInline
from custom_user.admin import EmailUserAdmin
from dateutil.relativedelta import relativedelta
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.admin import GenericStackedInline
from django.db.models import Count, Q
from django.http import HttpResponse
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.contrib.auth.admin import UserAdmin
from prevencija.models import User, Child, VolunteerReport
from admin_interface.admin import ThemeAdmin
from admin_interface.models import Theme

class AdminSite(admin.AdminSite):
    site_header = 'Prevencija administration'


admin_site = AdminSite()

class BaseAdmin(admin.ModelAdmin):

    allowed_actions = ['ADD', 'CHANGE', 'NO_CHANGE', 'CHANGE_OWN', 'DELETE', 'NO_DELETE', 'DELETE_OWN', 'VIEW', 'VIEW_OWN']
    def check_perm(self, user_obj, action=None):
        if not user_obj.is_active:
            return False
        if user_obj.is_superuser:
            return True
        if user_obj.is_staff and (action is None or action in self.allowed_actions):
            return True
        return False

    def has_add_permission(self, request):
        return self.check_perm(request.user, 'ADD')

    def has_change_permission(self, request, obj=None):
        return (self.check_perm(request.user, 'CHANGE') or self.check_perm(request.user, 'CHANGE_OWN')) and not 'NO_CHANGE' in self.allowed_actions

    def has_delete_permission(self, request, obj=None):
        return self.check_perm(request.user, 'DELETE') or self.check_perm(request.user, 'DELETE_OWN') and not 'NO_DELETE' in self.allowed_actions
    
    def has_module_permission(self, request, obj=None):
        return self.check_perm(request.user) 
    
    def has_view_permission(self, request, obj=None):
        return self.check_perm(request.user, 'VIEW') or self.check_perm(request.user, 'VIEW_OWN')

@admin.register(Theme, site=admin_site)
class AdminThemeAdmin(BaseAdmin, ThemeAdmin):
    allowed_actions = ['NONE']

@admin.register(User, site=admin_site)
class UserAdmin(BaseAdmin, EmailUserAdmin):
    """
    Is a necessity to render fieldsets and add_fieldsets otherwise focus_package
    is not displayed in form and as a result we can't add or edit it.
    """
    allowed_actions = ['VIEW_OWN']
    fieldsets = (
        (
            None, {
                'fields': (
                    'email',
                    'password',
                ),
            },
        ),
        (
            'Personal Info', {
                'fields': (
                    'first_name',
                    'last_name',
                    'jmbg',
                    'gender',
                ),
            },
        ),
        (
            'Permissions', {
                'fields': (
                    'is_active',
                    'is_superuser',
                ),
            },
        ),
        (
            'Important dates', {
                'fields': (
                    'last_login',
                    'date_joined',
                ),
            }
        ),
    )
    add_fieldsets = ((
        None, {
            'classes': ('wide',),
            'fields': ('email','password1', 'password2', 'first_name', 'last_name', 'jmbg', 'gender',)
        }
    ),
    )

    ordering = ['-jmbg']
    search_fields = (
        'first_name',
        'last_name',
        'jmbg',
        'email',
    )
    list_filter = (
        'gender',
    )
    list_display = (
        'email',
        'first_name',
        'last_name',
        'jmbg',
        'gender',
    )

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(pk=request.user.id)


    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            obj.is_staff = True
            obj.save()


@admin.register(Child, site=admin_site)
class ChildAdmin(BaseAdmin):
    allowed_actions = ['VIEW']
    list_display = (
        'jmbg',
        'first_name',
        'last_name',
        'gender',
    )
    search_fields = (
        'jmbg',
        'first_name',
        'last_name'
    )
    list_filter = (
        'gender',
    )
    fields = (
        'jmbg',
        'first_name',
        'last_name',
        'gender',
    )


@admin.register(VolunteerReport, site=admin_site)
class VolunteerReportAdmin(BaseAdmin):
    allowed_actions = ['NO_DELETE', 'VIEW_OWN']
    list_display = (
        'get_user',
        'get_child',
        'completed'
    )
    search_fields = (
        'volunteer__email',
        'volunteer__jmbg',
        'child__email',
        'child__jmbg',
    )
    list_filter = (
        'completed',
    )

    fieldsets = (
        (
            None, {
                'fields': (
                    'volunteer',
                    'child',
                    'date_completed',
                    'completed',
                    'report',
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ('volunteer', 'child',
                           ),
            }
        ),
    )

    def get_queryset(self, request):
        qs = super(VolunteerReportAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(volunteer=request.user)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['date_completed']
    
        readonly_fields = ['volunteer', 'child', 'date_completed', 'completed']

        return readonly_fields

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            input_date = obj.date_completed if obj.date_completed is not None else datetime.now()
            obj.date_completed = input_date if obj.completed else None
        obj.save()
    
    def render_change_form(self, request, context, *args, **kwargs):
        if (context['adminform'].form.fields.get('child', None) is None):
            context['adminform'].form.fields['child'].queryset = Child.objects.exclude(
                pk__in=VolunteerReport.objects.filter(completed=False).values_list('child', flat=True))
        return super(VolunteerReportAdmin, self).render_change_form(request, context, *args, **kwargs)

    def get_user(self, obj):
        return obj.volunteer.first_name + " " + obj.volunteer.last_name
    get_user.admin_order_field = 'user__jmbg'
    get_user.short_description = 'Volunteer'

    def get_child(self, obj):
        return obj.child.first_name + " " + obj.child.last_name
    get_child.admin_order_field = 'child__jmbg'
    get_child.short_description = 'Child'
