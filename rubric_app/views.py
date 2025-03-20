from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Subject, Rubric, Marks, Student, Teacher, Classroom
from .forms import CustomUserCreationForm, RubricUploadForm, ClassroomForm, JoinClassroomForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
import xlwt
import uuid
import os
from gradio_client import Client, handle_file
import csv
from .forms import StudentProfileForm


from django.conf import settings

def custom_login(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    else:
        return auth_views.LoginView.as_view(template_name='login.html')(request, *args, **kwargs)

# Dashboard redirect view to determine user type
@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.is_teacher:
        return redirect('teacher_dashboard')
    elif request.user.is_student:
        return redirect('student_dashboard')
    else:
        return redirect('login')

# Student dashboard view
@login_required
def student_dashboard(request):
    student = request.user.student
    classrooms = student.classrooms.all()
    join_form = JoinClassroomForm()

    # Assign a home URL based on the user role
    home_url = reverse('student_dashboard')

    # Assign light colors to classrooms
    light_colors = ["#f0f0f0", "#e0e0f0", "#d0d0f0", "#c0c0f0", "#b0b0f0"]
    for idx, classroom in enumerate(classrooms):
        classroom.color = light_colors[idx % len(light_colors)]

    if request.method == 'POST' and 'join_classroom' in request.POST:
        join_form = JoinClassroomForm(request.POST)
        if join_form.is_valid():
            code = join_form.cleaned_data['code']
            try:
                classroom = Classroom.objects.get(code=code)
                student.classrooms.add(classroom)
                messages.success(request, "Joined classroom successfully!")
            except Classroom.DoesNotExist:
                join_form.add_error('code', 'Invalid code')

    return render(
        request,
        'student_dashboard.html',
        {
            'classrooms': classrooms,
            'join_form': join_form,
            'home_url': home_url,
        },
    )
@login_required
def student_profile(request):
    student = get_object_or_404(Student, user=request.user)
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'student_profile.html', {
        'form': form,
        'student': student,
        'classrooms': student.classrooms.all()
    })
@login_required
def delete_rubric(request, rubric_id):
    rubric = get_object_or_404(Rubric, id=rubric_id, student=request.user.student)
    if request.method == 'POST':
        rubric.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

# Teacher dashboard view with classroom creation functionality
@login_required

def teacher_dashboard(request):
    teacher = request.user.teacher
    classrooms = Classroom.objects.filter(teacher=teacher)
    create_form = ClassroomForm()

    if request.method == 'POST':
        create_form = ClassroomForm(request.POST)
        if create_form.is_valid():
            classroom = create_form.save(commit=False)
            classroom.teacher = teacher
            classroom.code = uuid.uuid4().hex[:10]  
            classroom.save()
            messages.success(request, f"Classroom created! Code: {classroom.code}")
            return redirect('teacher_dashboard')
        else:
            messages.error(request, "Failed to create classroom. Please check the details.")

    return render(request, 'teacher_dashboard.html', {
        'classrooms': classrooms,
        'create_form': create_form
    })

    
# View classroom details for teacher, displaying enrolled students and their rubrics
@login_required
def get_enrolled_students(request, classroom_id):
    # Fetch the classroom, accessible to both students and teachers
    classroom = get_object_or_404(Classroom, id=classroom_id)
    
    # Ensure the user has access to the classroom
    if request.user.is_teacher and classroom.teacher.user != request.user:
        return JsonResponse({'error': 'You do not have access to this classroom'}, status=403)
    if request.user.is_student and not request.user.student.classrooms.filter(id=classroom_id).exists():
        return JsonResponse({'error': 'You are not enrolled in this classroom'}, status=403)
    
    # Fetch the list of enrolled students
    students = classroom.students.all().values_list('user__username', flat=True)
    return JsonResponse({'students': list(students)})


@login_required
def view_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    context = {'classroom': classroom}

    if request.user.is_teacher:
        # Ensure the teacher owns the classroom
        teacher = request.user.teacher
        if classroom.teacher != teacher:
            messages.error(request, "You do not have permission to view this classroom.")
            return redirect("teacher_dashboard")

        # Fetch students and rubrics
        students = classroom.students.all()
        rubrics = Rubric.objects.filter(classroom=classroom)

        # Add to the context
        context["students"] = students
        context["rubrics"] = rubrics
        context["is_teacher"] = True

    elif request.user.is_student:
        # Ensure the student is enrolled in the classroom
        student = request.user.student
        if not student.classrooms.filter(id=classroom_id).exists():
            messages.error(request, "You are not part of this classroom.")
            return redirect("student_dashboard")

        # Fetch rubrics for the logged-in student
        rubrics = Rubric.objects.filter(classroom=classroom, student=student)

        # Add to the context
        context["rubrics"] = rubrics
        context["students"] = classroom.students.all()  # Allow students to view enrolled peers
        context["is_student"] = True
        
        

    else:
        messages.error(request, "Invalid user role.")
        return redirect("dashboard_redirect")

    return render(request, "view_classroom.html", context)


@login_required
def export_grades(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    
    if not request.user.is_teacher or classroom.teacher.user != request.user:
        return HttpResponse('Unauthorized', status=401)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{classroom.name}_grades.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Grades')

    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Student', 'Knowledge', 'Performance', 'Content & Neatness', 'Punctuality', 'Total Marks']
    
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rubrics = Rubric.objects.filter(classroom=classroom).select_related('student__user')
    
    for rubric in rubrics:
        row_num += 1
        ws.write(row_num, 0, rubric.student.user.username, font_style)
        ws.write(row_num, 1, rubric.knowledge or 0, font_style)
        ws.write(row_num, 2, rubric.performance or 0, font_style)
        ws.write(row_num, 3, rubric.content_neatness or 0, font_style)
        ws.write(row_num, 4, rubric.punctuality_submission or 0, font_style)
        ws.write(row_num, 5, rubric.total_marks or 0, font_style)

    wb.save(response)
    return response

# ---------------------- Rubric Processing ----------------------
def delete_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, teacher=request.user.teacher)
    
    if request.method == 'POST':
        classroom.delete()  # Delete the classroom
        return redirect('teacher_dashboard')  # Redirect to the teacher dashboard after deletion

    return redirect('teacher_dashboard')  # Fallback
# View student rubrics for a specific classroom, accessible by the teacher
@login_required
def view_student_rubrics(request, classroom_id, student_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, teacher=request.user.teacher)
    student = get_object_or_404(Student, id=student_id, classrooms=classroom)
    rubrics = Rubric.objects.filter(student=student, classroom=classroom)
    return render(request, 'upload_rubrics.html', {
        'classroom': classroom,
        'student': student,
        'rubrics': rubrics
    })

# Admin dashboard (if applicable)
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# Join classroom view
@login_required
def join_classroom(request):
    if request.method == 'POST':
        join_form = JoinClassroomForm(request.POST)
        if join_form.is_valid():
            code = join_form.cleaned_data['code']
            classroom = get_object_or_404(Classroom, code=code)
            student = request.user.student
            student.classrooms.add(classroom)
            messages.success(request, "Successfully joined the classroom!")
            return redirect('student_dashboard')
    return redirect('student_dashboard')
@login_required
def upload_rubric(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, students=request.user.student)
    
    if request.method == 'POST':
        form = RubricUploadForm(request.POST, request.FILES)
        if form.is_valid():
            rubric_file = request.FILES['rubric_file']
            file_path = os.path.join('media/rubrics', rubric_file.name)
            
            # Save rubric file locally
            with open(file_path, 'wb+') as destination:
                for chunk in rubric_file.chunks():
                    destination.write(chunk)

            # Initialize the Gradio Client only when necessary
            try:
                # Lazy-load the Client here
                client = Client("13bit/rubricease", hf_token="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")

                # Call the Gradio API for mark extraction
                result = client.predict(
                    img=handle_file(file_path),  # Assuming handle_file function processes the image
                    api_name="/predict",
                )
                #print(result)

                # Unpack the result (adjust according to your API response)
                image_path, knowledge, performance, content_neatness, punctuality_submission, total = result
                total=int(knowledge)+int(performance)+int(content_neatness)+int(punctuality_submission)
                # Delay saving the rubric to assign additional fields
                rubric = form.save(commit=False)
                rubric.classroom = classroom  # Assign the classroom foreign key
                rubric.student = request.user.student  # Assign the student foreign key
                rubric.knowledge = knowledge
                rubric.performance = performance
                rubric.content_neatness = content_neatness
                rubric.punctuality_submission = punctuality_submission
                rubric.total_marks = total
                rubric.save()

                # Optionally create associated marks
                Marks.objects.create(rubric=rubric)

                # Return success response
                response_data = {
                    'success': True,
                    'imageUrl': rubric.rubric_file.url,
                    'knowledge': knowledge,
                    'performance': content_neatness,
                    'content_neatness': performance,
                    'punctuality_submission': punctuality_submission,
                    'total_marks': total,
                }
                return JsonResponse(response_data)

            except Exception as e:
                # Log the error for easier debugging
                
                return JsonResponse({'success': False, 'message': 'Error in uploading rubric! Please try again.'})

    else:
        form = RubricUploadForm()

    return render(request, 'upload_rubric.html', {'form': form, 'classroom': classroom})

# ---------------------- Registration Views ----------------------

# Student registration
def student_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_student = True
            user.save()
            Student.objects.create(user=user)
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'student_register.html', {'form': form})

@login_required
def unenroll_from_classroom(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    student = request.user.student
    
    if classroom.students.filter(id=student.id).exists():
        classroom.students.remove(student)  # Remove the student from the classroom
        return redirect('student_dashboard')  # Redirect back to the student dashboard after unenrollment

    return redirect('student_dashboard')  # Fallback

# Teacher registration
def teacher_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_teacher = True
            user.save()
            Teacher.objects.create(user=user)
            login(request, user)
            return redirect('teacher_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'teacher_register.html', {'form': form})

# --    -------------------- Admin Views ----------------------

