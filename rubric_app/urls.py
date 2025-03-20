from django.urls import path
from django.views.generic.base import RedirectView  # Import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings  # Import settings
from django.conf.urls.static import static  # Import static
from . import views
from .views import delete_classroom, unenroll_from_classroom, upload_rubric  # Import views
from .views import delete_rubric  # Import delete_rubric view
from .views import student_profile

urlpatterns = [
    path('', RedirectView.as_view(url='login', permanent=False), name='home'),
    path('login/', views.custom_login, name='login'),  # Use custom login view
    path('teacher_login/', auth_views.LoginView.as_view(template_name='teacher_login.html'), name='teacher_login'),
    path('student_register/', views.student_register, name='student_register'),
    path('teacher_register/', views.teacher_register, name='teacher_register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('join_classroom/', views.join_classroom, name='join_classroom'),
    path('dashboard_redirect/', views.dashboard_redirect, name='dashboard_redirect'),
    path('classroom/<int:classroom_id>/student/<int:student_id>/', views.view_student_rubrics, name='view_student_rubrics'),
    path('upload_rubric/<int:classroom_id>/', views.upload_rubric, name='upload_rubric'),  # Ensure classroom_id is correctly defined
    path('classroom/<int:classroom_id>/', views.view_classroom, name='view_classroom'),
    path('classroom/<int:classroom_id>/unenroll/', unenroll_from_classroom, name='unenroll_from_classroom'),
    path('rubric/<int:rubric_id>/delete/', delete_rubric, name='delete_rubric'),
    path('classroom/<int:classroom_id>/delete/', delete_classroom, name='delete_classroom'),
    path('get_enrolled_students/<int:classroom_id>/', views.get_enrolled_students, name='get_enrolled_students'),
    path('classroom/<int:classroom_id>/export/', views.export_grades, name='export_grades'),
    path('student/profile/', student_profile, name='student_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
