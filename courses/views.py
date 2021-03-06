# imports from my apps
from .models import Course, Module, Content, Subject
from .forms import ModuleFormSet

# imports from django
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateResponseMixin, View
from django.forms.models import modelform_factory
from django.apps import apps
from django.db.models import Count

# imports from 3rd packcage
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin


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
    fields = ["title", "slug", "subject", "overview"]
    success_url = reverse_lazy("owner_course_list")


class OwnerCourseEditMixin(OwnerEditMixin, OwnerCourseMixin):
    template_name = "owner/course/form.html"


class OwnerCourseList(OwnerCourseMixin, ListView):
    template_name = "owner/course/list.html"
    permission_required = "courses.view_course"
    # model = Course
    # template_name = 'courses/owner/list.html'

    # def get_queryset(self) -> QuerySet[T]:
    #     qs = super().get_queryset()
    #     return qs.filter(owner = self.request.user)


class OwnerCourseCreate(OwnerCourseEditMixin, CreateView):
    permission_required = "courses.add_course"


class OwnerCourseUpdate(OwnerCourseEditMixin, UpdateView):
    permission_required = "courses.change_course"


class OwnerCourseDelete(OwnerCourseMixin, DeleteView):
    template_name = "owner/course/delete.html"
    permission_required = "courses.delete_course"


class OwnerCourseModuleUpdate(TemplateResponseMixin, View):
    template_name = "owner/module/formset.html"
    course = None

    def get_formest(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formest()
        return self.render_to_response({"course": self.course, "formset": formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formest(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("owner_course_list")
        return self.render_to_response({"course": self.course, "formset": formset})


class ContentCreateUpdate(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = "owner/content/form.html"

    def get_model(self, model_name):
        if model_name in ["text", "file", "video", "image"]:
            return apps.get_model(app_label="courses", model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=["owner", "order", "created", "updated"]
        )
        return Form(*args, **kwargs)

    def dispatch(self, request, model_name, module_id, id=None):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(
                self.model,
                id=id,
                owner=request.user,
            )
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({"form": form, "object": self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(
            self.model, instance=self.obj, data=request.POST, files=request.FILES
        )

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                Content.objects.create(module=self.module, item=obj)
            return redirect("module_content_list", self.module.id)
        return self.render_to_response({"form": form, "object": self.obj})


class ContentDelete(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect("module_content_list", module.id)


class ModuleContentList(TemplateResponseMixin, View):
    template_name = "owner/module/content_list.html"

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)

        return self.render_to_response({"module": module})


class ModuleOrder(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(
                id=id,
                course__owner=request.user,
            ).update(order=order)
        return self.render_json_response({"saved": "ok"})


class ContentOrder(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(
                id=id,
                module__course__owner=request.user,
            ).update(order=order)
        return self.render_json_response({"saved": "ok"})


class CourseList(TemplateResponseMixin, View):
    model = Course
    template_name = "course/list.html"

    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(total_courses=Count("courses"))
        courses = Course.objects.annotate(total_modules=Count("modules"))
        if subject:
            try:
                subject = get_object_or_404(Subject, slug=subject)
            except Subject.DoesNotExist:
                print("the provided slug isnt correct")
            courses = courses.filter(subject=subject)
        return self.render_to_response(
            {"subjects": subjects, "subject": subject, "courses": courses}
        )


class CourseDetails(DetailView):
    template_name = "course/details.html"
    model = Course
