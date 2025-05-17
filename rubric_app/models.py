import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Subject(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Default Name')
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(blank=True, null=True)
    branch = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=10, unique=True, default=uuid.uuid4().hex[:10])

    # ✅ Many-to-Many relationship (Reverse Access Preserved)
    students = models.ManyToManyField("Student", blank=True, related_name="classrooms")  

    def __str__(self):
        return f"{self.name} ({self.code})"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    roll_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,  # ✅ Allow database NULL values to prevent conflicts
        help_text="Unique identifier for the student across all classrooms"
    )
    full_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.roll_number or 'No Roll'} - {self.full_name or self.user.username}"

    # 🚫 Removed duplicate classrooms field (Handled by Classroom.students)

    def __str__(self):
        return f"{self.roll_number} - {self.full_name or self.user.username}"


# ✅ Rubric Model
class Rubric(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="rubrics", blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="rubrics", null=True)
    rubric_file = models.ImageField(upload_to="rubrics/", blank=True, null=True)
    experiment_number = models.IntegerField(default=1, choices=[(i, f"Lab {i}") for i in range(1, 11)])
    knowledge = models.IntegerField(default=0, blank=True, null=True)
    performance = models.IntegerField(default=0, blank=True, null=True)
    content_neatness = models.IntegerField(default=0, blank=True, null=True)
    punctuality_submission = models.IntegerField(default=0, blank=True, null=True)
    total_marks = models.IntegerField(default=0, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Rubric for {self.student.user.username} in {self.classroom.name if self.classroom else 'No Classroom'} - Lab {self.experiment_number}"

# ✅ Marks Model
class Marks(models.Model):
    rubric = models.OneToOneField(Rubric, on_delete=models.CASCADE)
    knowledge = models.IntegerField(default=0)
    performance = models.IntegerField(default=0)
    content_neatness = models.IntegerField(default=0)
    punctuality_submission = models.IntegerField(default=0)

    def __str__(self):
        return f"Marks for {self.rubric.student.full_name or self.rubric.student.user.username} in {self.rubric.classroom.name if self.rubric.classroom else 'No Classroom'}"
