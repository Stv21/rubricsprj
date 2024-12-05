from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a new user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('password', type=str, help='Password of the user')
        parser.add_argument('--is_student', action='store_true', help='Create a student user')
        parser.add_argument('--is_teacher', action='store_true', help='Create a teacher user')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        is_student = kwargs['is_student']
        is_teacher = kwargs['is_teacher']

        User = get_user_model()
        user = User.objects.create_user(username=username, password=password)
        user.is_student = is_student
        user.is_teacher = is_teacher
        user.save()

        self.stdout.write(self.style.SUCCESS(f'User {username} created successfully'))