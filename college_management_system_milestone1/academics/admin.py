from django.contrib import admin
from .models import (
    Assessment,
    Assignment,
    Attendance,
    Course,
    Department,
    Enrollment,
    Result,
    Student,
    Teacher,
    Notice,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "duration_years")
    list_filter = ("department", "duration_years")
    search_fields = ("name", "code", "department__name")

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("roll_number", "user", "department", "admission_date")
    list_filter = ("department", "admission_date")
    search_fields = (
        "roll_number",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "department", "joining_date")
    list_filter = ("department", "joining_date")
    search_fields = (
        "employee_id",
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    filter_horizontal = ("courses",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "academic_year",
        "status",
        "enrolled_on",
    )
    list_filter = ("academic_year", "status", "course__department")
    search_fields = (
        "student__roll_number",
        "student__user__username",
        "course__name",
        "course__code",
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "attendance_date",
        "status",
    )
    list_filter = (
        "status",
        "attendance_date",
        "enrollment__course",
    )
    search_fields = (
        "enrollment__student__roll_number",
        "enrollment__course__code",
        "enrollment__student__user__username",
    )
    date_hierarchy = "attendance_date"

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "exam_date", "max_marks")
    list_filter = ("course", "exam_date")
    search_fields = ("title", "course__name", "course__code")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "assessment", "marks_obtained")
    list_filter = ("assessment__course", "assessment")
    search_fields = (
        "enrollment__student__roll_number",
        "assessment__title",
        "assessment__course__code",
    )

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "teacher", "due_date", "posted_on")
    list_filter = ("course", "teacher", "due_date")
    search_fields = ("title", "course__name", "course__code")

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "teacher", "important", "posted_on")
    list_filter = ("course", "teacher", "important", "posted_on")
    search_fields = ("title", "message", "course__name", "course__code")