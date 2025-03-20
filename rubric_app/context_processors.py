from .models import Classroom, Student

def classrooms(request):
    context = {'classrooms': []}
    if request.user.is_authenticated:
        if hasattr(request.user, 'teacher'):
            context['classrooms'] = Classroom.objects.filter(teacher=request.user.teacher)
        elif hasattr(request.user, 'student'):
            context['classrooms'] = request.user.student.classrooms.all()
    return context