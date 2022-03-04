from typing import List
from django.shortcuts import render
from .models import Course
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user 
        return super().form_valid()

class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = ['title', 'slug', 'subject','overview']
    success_url = reverse_lazy('owner_course_list')

class OwnerCourseEditMixin(OwnerEditMixin, OwnerCourseMixin):
    template_name = 'courses/owner/course/form.html'


class OwnerCourseList(OwnerCourseMixin, ListView):
    template_name = 'courses/owner/course/list.html'
    permission_required = 'courses.view_course'
    # model = Course
    # template_name = 'courses/owner/list.html'

    # def get_queryset(self) -> QuerySet[T]:
    #     qs = super().get_queryset()
    #     return qs.filter(owner = self.request.user)

class OwnerCourseCreate(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

class OwnerCourseUpdate(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

class OwnerCourseDelete(OwnerCourseMixin, DeleteView):
    permission_required = 'courses.delete_course'







