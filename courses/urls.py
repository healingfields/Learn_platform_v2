from django.urls import path
from . import views



urlpatterns = [
    path('mine/', views.OwnerCourseList.as_view(), name='owner_course_list'),
    path('create/', views.OwnerCourseCreate.as_view(), name='course_create'),
    path('<pk>/edit', views.OwnerCourseUpdate.as_view(), name='course_edit'),
    path('<pk>/delete', views.OwnerCourseDelete.as_view(), name='course_delete')
]