from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=150)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name='courses', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return f'name:{self.title}, made by {self.owner}'

class Module(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title
