from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField


class Subject(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=150)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(
        Subject, related_name="courses", on_delete=models.CASCADE
    )
    owner = models.ForeignKey(User, related_name="courses", on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"name:{self.title}, made by {self.owner}"


class Module(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField()
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    order = OrderField(blank=True, for_fields=["course"])

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.title}, {self.order}"


class Content(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            "model__in": (
                "text",
                "video",
                "image",
            )
        },
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    module = models.ForeignKey(
        Module, related_name="contents", on_delete=models.CASCADE
    )
    order = OrderField(blank=True, for_fields=["module"])

    class Meta:
        ordering = ["order"]


class ItemBase(models.Model):
    title = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, related_name="%(class)s_related", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to="files")


class Image(ItemBase):
    image = models.FileField(upload_to="images")


class Video(ItemBase):
    url = models.URLField()
