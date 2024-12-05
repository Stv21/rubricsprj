from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Student, Teacher

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_student:
            Student.objects.create(user=instance)
        elif instance.is_teacher:
            Teacher.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_student:
        instance.student.save()
    elif instance.is_teacher:
        instance.teacher.save()