from django.contrib import admin

from .models import (
    EducationProfile,
    Class,
    Subject,
    Chapter,
    Lesson,
)


@admin.register(EducationProfile)
class EducationProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "created_at",
    )


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order",
    )

    ordering = ("order",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "class_level",
    )

    list_filter = (
        "class_level",
    )


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "subject",
        "chapter_number",
    )

    list_filter = (
        "subject",
    )

    ordering = (
        "subject",
        "chapter_number",
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "chapter",
        "lesson_number",
        "video",
    )

    list_filter = (
        "chapter",
    )

    search_fields = (
        "title",
        "chapter__name",
    )