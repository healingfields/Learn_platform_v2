from unicodedata import name
from django.urls import path
from . import views


urlpatterns = [
    path("mine/", views.OwnerCourseList.as_view(), name="owner_course_list"),
    path("create/", views.OwnerCourseCreate.as_view(), name="course_create"),
    path("<pk>/edit", views.OwnerCourseUpdate.as_view(), name="course_edit"),
    path("<pk>/delete", views.OwnerCourseDelete.as_view(), name="course_delete"),
    path(
        "<pk>/module/",
        views.OwnerCourseModuleUpdate.as_view(),
        name="course_module_update",
    ),
    path(
        "module/<int:module_id>/content/<model_name>/create/",
        views.ContentCreateUpdate.as_view(),
        name="module_content_create",
    ),
    path(
        "module/<int:module_id>/content/<model_name>/<int:id>/",
        views.ContentCreateUpdate.as_view(),
        name="module_content_update",
    ),
    path(
        "content/<int:id>/delete/",
        views.ContentDelete.as_view(),
        name="module_content_delete",
    ),
]
