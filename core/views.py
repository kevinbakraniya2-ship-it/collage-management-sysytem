from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from academics.models import Department, Student, Teacher, Enrollment

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import redirect

from academics.forms import AttendanceForm, ResultForm
from django.core.paginator import Paginator
from django.db.models import Q

from django.http import FileResponse
from django.shortcuts import get_object_or_404

from academics.forms import AssignmentForm
from academics.models import Assignment

from academics.forms import NoticeForm
from academics.models import Notice

def home(request):
    if request.user.is_authenticated:
        try:
            request.user.teacher_profile
            return redirect("teacher_dashboard")
        except Teacher.DoesNotExist:
            pass
        try:
            request.user.student_profile
            return redirect("student_dashboard")
        except Student.DoesNotExist:
            pass
    departments = Department.objects.prefetch_related("courses")
    return render(
        request,
        "core/home.html",
        {"departments": departments},
    )


def custom_logout(request):
    """Logout user on both GET and POST to avoid CSRF 403 errors."""
    auth_logout(request)
    return redirect("login")


@login_required
def student_dashboard(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        raise PermissionDenied

    enrollments = (
    student.enrollments
    .select_related("course")
    .prefetch_related("attendance_records", "results__assessment")
)
    return render(
        request,
        "core/student_dashboard.html",
        {
            "student": student,
            "enrollments": enrollments,
        },
    )


@login_required
def teacher_dashboard(request):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    courses = teacher.courses.all()
    assignments = (
        Assignment.objects
        .filter(teacher=teacher)
        .select_related("course")
        .order_by("-posted_on")
    )
    notices = (
        Notice.objects
        .filter(teacher=teacher)
        .select_related("course")
        .order_by("-posted_on")
    )

    return render(
        request,
        "core/teacher_dashboard.html",
        {
            "teacher": teacher,
            "courses": courses,
            "assignments": assignments,
            "notices": notices,
        },
    )

@login_required
def mark_attendance(request):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    form = AttendanceForm(
        request.POST or None,
        teacher=teacher,
    )

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error(
                None,
                "Is Enrollment ki attendance is date par pehle se maujood hai.",
            )
        else:
            messages.success(request, "Attendance save ho gayi.")
            return redirect("mark_attendance")

    return render(
        request,
        "core/mark_attendance.html",
        {"form": form},
    )

@login_required
def enter_result(request):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    form = ResultForm(
        request.POST or None,
        teacher=teacher,
    )

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error(
                None,
                "Is Enrollment ka Result is Assessment ke liye pehle se maujood hai.",
            )
        else:
            messages.success(request, "Result save ho gaya.")
            return redirect("enter_result")

    return render(
        request,
        "core/enter_result.html",
        {"form": form},
    )

@login_required
def teacher_students(request):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    query = request.GET.get("q", "").strip()

    enrollments = (
        Enrollment.objects
        .filter(course__teachers=teacher)
        .select_related("student__user", "course")
        .order_by(
            "student__roll_number",
            "course__code",
            "academic_year",
        )
    )

    if query:
        enrollments = enrollments.filter(
            Q(student__roll_number__icontains=query)
            | Q(student__user__username__icontains=query)
            | Q(student__user__first_name__icontains=query)
            | Q(student__user__last_name__icontains=query)
            | Q(course__name__icontains=query)
            | Q(course__code__icontains=query)
        )

    page_obj = Paginator(enrollments, 10).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "core/teacher_students.html",
        {
            "page_obj": page_obj,
            "query": query,
        },
    )

@login_required
def post_assignment(request):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    form = AssignmentForm(
        request.POST or None,
        request.FILES or None,
        teacher=teacher,
    )

    if request.method == "POST" and form.is_valid():
        assignment = form.save(commit=False)
        assignment.teacher = teacher
        assignment.save()
        messages.success(request, "Assignment upload ho gaya.")
        return redirect("post_assignment")

    return render(
        request,
        "core/post_assignment.html",
        {"form": form},
    )


@login_required
def student_assignments(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        raise PermissionDenied

    assignments = (
        Assignment.objects
        .filter(course__enrollments__student=student)
        .select_related("course", "teacher__user")
        .distinct()
    )

    return render(
        request,
        "core/student_assignments.html",
        {"assignments": assignments},
    )


@login_required
def download_assignment(request, pk):
    assignment = get_object_or_404(
        Assignment.objects.select_related("course", "teacher"),
        pk=pk,
    )

    allowed = request.user.is_staff

    if not allowed:
        try:
            teacher = request.user.teacher_profile
        except Teacher.DoesNotExist:
            teacher = None

        if teacher is not None:
            allowed = assignment.course.teachers.filter(pk=teacher.pk).exists()

        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            student = None

        if student is not None:
            allowed = allowed or assignment.course.enrollments.filter(
                student=student
            ).exists()

    if not allowed:
        raise PermissionDenied

    return FileResponse(
        assignment.file.open("rb"),
        as_attachment=True,
        filename=assignment.file.name.rsplit("/", 1)[-1],
        content_type="application/pdf",
    )

@login_required
def post_notice(request):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    form = NoticeForm(
        request.POST or None,
        teacher=teacher,
    )

    if request.method == "POST" and form.is_valid():
        notice = form.save(commit=False)
        notice.teacher = teacher
        notice.save()
        messages.success(request, "Notice post ho gaya.")
        return redirect("post_notice")

    return render(
        request,
        "core/post_notice.html",
        {"form": form},
    )


@login_required
def edit_assignment(request, pk):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    assignment = get_object_or_404(Assignment, pk=pk, teacher=teacher)
    form = AssignmentForm(
        request.POST or None,
        request.FILES or None,
        instance=assignment,
        teacher=teacher,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Assignment update ho gaya.")
        return redirect("teacher_dashboard")

    return render(
        request,
        "core/edit_assignment.html",
        {"form": form, "assignment": assignment},
    )


@login_required
def delete_assignment(request, pk):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    assignment = get_object_or_404(Assignment, pk=pk, teacher=teacher)
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment delete ho gaya.")
        return redirect("teacher_dashboard")

    return render(
        request,
        "core/confirm_delete.html",
        {"item": assignment, "item_type": "Assignment"},
    )


@login_required
def edit_notice(request, pk):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    notice = get_object_or_404(Notice, pk=pk, teacher=teacher)
    form = NoticeForm(
        request.POST or None,
        instance=notice,
        teacher=teacher,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Notice update ho gaya.")
        return redirect("teacher_dashboard")

    return render(
        request,
        "core/edit_notice.html",
        {"form": form, "notice": notice},
    )


@login_required
def delete_notice(request, pk):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    notice = get_object_or_404(Notice, pk=pk, teacher=teacher)
    if request.method == "POST":
        notice.delete()
        messages.success(request, "Notice delete ho gaya.")
        return redirect("teacher_dashboard")

    return render(
        request,
        "core/confirm_delete.html",
        {"item": notice, "item_type": "Notice"},
    )


@login_required
def teacher_history(request):
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        raise PermissionDenied

    assignments = (
        Assignment.objects
        .filter(teacher=teacher)
        .select_related("course")
        .order_by("-posted_on")
    )
    notices = (
        Notice.objects
        .filter(teacher=teacher)
        .select_related("course")
        .order_by("-posted_on")
    )
    from academics.models import Attendance, Result
    attendances = (
        Attendance.objects
        .filter(enrollment__course__teachers=teacher)
        .select_related("enrollment__student__user", "enrollment__course")
        .order_by("-attendance_date")[:50]
    )
    results = (
        Result.objects
        .filter(assessment__course__teachers=teacher)
        .select_related(
            "enrollment__student__user",
            "assessment__course",
        )
        .order_by("-assessment__exam_date")[:50]
    )

    return render(
        request,
        "core/teacher_history.html",
        {
            "teacher": teacher,
            "assignments": assignments,
            "notices": notices,
            "attendances": attendances,
            "results": results,
        },
    )


@login_required
def student_notices(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        raise PermissionDenied

    notices = (
        Notice.objects
        .filter(course__enrollments__student=student)
        .select_related("course", "teacher__user")
        .distinct()
    )

    return render(
        request,
        "core/student_notices.html",
        {"notices": notices},
    )