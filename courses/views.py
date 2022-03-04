from re import template
from typing import List
from django.shortcuts import render
from .models import Course, Module
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet

class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user 
        return super().form_valid(form)

class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = ['title', 'slug', 'subject','overview']
    success_url = reverse_lazy('owner_course_list')

class OwnerCourseEditMixin(OwnerEditMixin, OwnerCourseMixin):
    template_name = 'owner/course/form.html'


class OwnerCourseList(OwnerCourseMixin, ListView):
    template_name = 'owner/course/list.html'
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
    template_name = 'owner/course/delete.html'
    permission_required = 'courses.delete_course'


class OwnerCourseModuleUpdate(TemplateResponseMixin, View):
    template_name = 'owner/module/formset.html'
    course = None

    def get_formest(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk) :
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)
    
    def get(self, request, *args, **kwargs):
        formset = self.get_formest()
        return self.render_to_response({'course':self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formest(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('owner_course_list')
        return self.render_to_response({'course':self.course, 'formset': formset}) 








