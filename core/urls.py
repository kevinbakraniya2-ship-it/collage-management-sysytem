from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path(
    "teacher/attendance/mark/",
    views.mark_attendance,
    name="mark_attendance",
    ),

    path(
    "teacher/results/add/",
    views.enter_result,
    name="enter_result",
    ),

    path(
    "teacher/students/",
    views.teacher_students,
    name="teacher_students",
    ),

    path(
    "teacher/assignments/add/",
    views.post_assignment,
    name="post_assignment",
    ),

    path(
    "student/assignments/",
    views.student_assignments,
    name="student_assignments",
    ),

    path(
    "assignments/<int:pk>/download/",
    views.download_assignment,
    name="download_assignment",
    ),

    path(
    "teacher/notices/add/",
    views.post_notice,
    name="post_notice",
    ),

    path(
    "student/notices/",
    views.student_notices,
    name="student_notices",
    ),

    path("teacher/assignments/<int:pk>/edit/", views.edit_assignment, name="edit_assignment"),
    path("teacher/assignments/<int:pk>/delete/", views.delete_assignment, name="delete_assignment"),
    path("teacher/notices/<int:pk>/edit/", views.edit_notice, name="edit_notice"),
    path("teacher/notices/<int:pk>/delete/", views.delete_notice, name="delete_notice"),
    path("teacher/history/", views.teacher_history, name="teacher_history"),
]
