from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Teacher, Subject, Rubric, Marks

admin.site.register(CustomUser, UserAdmin)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'full_name', 'user']
    search_fields = ['roll_number', 'full_name']

admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Rubric)
admin.site.register(Marks)