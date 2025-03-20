from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Rubric, Classroom
from datetime import datetime
from .models import Student

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('is_student', 'is_teacher')

class RubricUploadForm(forms.ModelForm):
    class Meta:
        model = Rubric
        fields = ['rubric_file']
        widgets = {
            'rubric_file': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }

class ClassroomForm(forms.ModelForm):
    BRANCH_CHOICES = [
        ('CE', 'Computer Engineering'),
        ('CSE', 'Computer Science and Engineering'),
        ('EXTC', 'Electronics and Telecommunication'),
        ('IT', 'Information Technology'),
    ]
    
    branch = forms.ChoiceField(choices=BRANCH_CHOICES, label='Branch', required=True)
    
    # Set the current year as the default value
    current_year = datetime.now().year
    year = forms.IntegerField(initial=current_year, label='Year', required=True)

    class Meta:
        model = Classroom
        fields = ['subject', 'name', 'year', 'branch']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Enter Subject Name'}),
            'name': forms.TextInput(attrs={'placeholder': 'Teacher\'s Name'}),
        }
class JoinClassroomForm(forms.Form):
    code = forms.CharField(max_length=10, label='Classroom Code')

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['roll_number', 'full_name']  # Add roll_number here
        labels = {
            'roll_number': 'Roll Number',
            'full_name': 'Full Name'
        }
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'roll_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your roll number'
            })
        }

