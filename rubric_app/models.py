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
    name = models.CharField(max_length=100, blank=True, null=True)  # Allow null
    year = models.IntegerField(blank=True, null=True)  # Allow null
    branch = models.CharField(max_length=100, blank=True, null=True)  # Allow null

    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Default Name')
    subjects = models.ManyToManyField(Subject, blank=True)  # Allow empty

    def __str__(self):
        return self.name

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)  # Free-text input for subject
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(blank=True, null=True)
    branch = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=10, unique=True, default=uuid.uuid4().hex[:10])

    def __str__(self):
        return f"{self.name} ({self.code})"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    classrooms = models.ManyToManyField(Classroom, blank=True, related_name="students")

    def __str__(self):
        return self.user.username

class Rubric(models.Model):
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="rubrics",
        blank=True,
        null=True
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="rubrics",
        null=True
    )
    rubric_file = models.ImageField(upload_to="rubrics/", blank=True, null=True)
    knowledge = models.IntegerField(default=0, blank=True, null=True)
    performance = models.IntegerField(default=0, blank=True, null=True)
    content_neatness = models.IntegerField(default=0, blank=True, null=True)
    punctuality_submission = models.IntegerField(default=0, blank=True, null=True)
    total_marks = models.IntegerField(default=0, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Rubric for {self.student.user.username} in {self.classroom.name if self.classroom else 'No Classroom'}"

class Marks(models.Model):
    rubric = models.OneToOneField(Rubric, on_delete=models.CASCADE)
    knowledge = models.IntegerField(default=0)
    performance = models.IntegerField(default=0)
    content_neatness = models.IntegerField(default=0)
    punctuality_submission = models.IntegerField(default=0)

    def __str__(self):
        return f"Marks for {self.rubric.student.user.username} in {self.rubric.classroom.name if self.rubric.classroom else 'No Classroom'}"
