from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Teacher, Subject, Rubric, Marks

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Rubric)
admin.site.register(Marks)