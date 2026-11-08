from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from .forms import AttendanceForm, ResultForm
from .models import (
    Assessment,
    Attendance,
    Course,
    Department,
    Enrollment,
    Student,
    Teacher,
)
from .forms import AttendanceForm, NoticeForm, ResultForm

class StudentModelTests(TestCase):
    def test_student_profile_links_user_and_department(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="student1",
            password="test-password-123",
            first_name="Asha",
        )
        department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )

        student = Student.objects.create(
            user=user,
            roll_number="CS001",
            department=department,
        )

        self.assertEqual(student.user, user)
        self.assertEqual(student.department, department)
        self.assertEqual(str(student), "CS001 — Asha")

class TeacherModelTests(TestCase):
    def test_teacher_links_user_department_and_course(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="teacher1",
            password="test-password-123",
            first_name="Ravi",
        )
        department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )
        course = Course.objects.create(
            name="Python Programming",
            code="PY101",
            department=department,
            duration_years=1,
        )

        teacher = Teacher.objects.create(
            user=user,
            employee_id="T001",
            department=department,
        )
        teacher.courses.add(course)

        self.assertEqual(teacher.user, user)
        self.assertEqual(teacher.department, department)
        self.assertIn(course, teacher.courses.all())
        self.assertEqual(str(teacher), "T001 — Ravi")

class EnrollmentModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="enrolled_student",
            password="test-password-123",
        )
        department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )
        self.student = Student.objects.create(
            user=user,
            roll_number="CS001",
            department=department,
        )
        self.course = Course.objects.create(
            name="Python Programming",
            code="PY101",
            department=department,
            duration_years=1,
        )

    def test_enrollment_connects_student_and_course(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            academic_year="2026-2027",
        )

        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertEqual(enrollment.status, Enrollment.Status.ACTIVE)

class AttendanceModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="attendance_student",
            password="test-password-123",
        )
        department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )
        student = Student.objects.create(
            user=user,
            roll_number="CS001",
            department=department,
        )
        course = Course.objects.create(
            name="Python Programming",
            code="PY101",
            department=department,
            duration_years=1,
        )
        self.enrollment = Enrollment.objects.create(
            student=student,
            course=course,
            academic_year="2026-2027",
        )

    def test_attendance_is_saved_for_enrollment(self):
        record = Attendance.objects.create(
            enrollment=self.enrollment,
            attendance_date=date(2026, 11, 1),
            status=Attendance.Status.PRESENT,
        )

        self.assertEqual(record.enrollment, self.enrollment)
        self.assertEqual(record.get_status_display(), "Present")

    def test_duplicate_daily_attendance_is_rejected(self):
        Attendance.objects.create(
            enrollment=self.enrollment,
            attendance_date=date(2026, 11, 1),
            status=Attendance.Status.PRESENT,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Attendance.objects.create(
                    enrollment=self.enrollment,
                    attendance_date=date(2026, 11, 1),
                    status=Attendance.Status.ABSENT,
                )

class AttendanceFormScopeTests(TestCase):
    def test_teacher_only_sees_enrollments_in_assigned_courses(self):
        user_model = get_user_model()

        department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )

        teacher_user = user_model.objects.create_user(
            username="teacher_scope_test",
            password="test-password-123",
        )
        teacher = Teacher.objects.create(
            user=teacher_user,
            employee_id="T-SCOPE",
            department=department,
        )

        allowed_course = Course.objects.create(
            name="Python",
            code="PY201",
            department=department,
            duration_years=1,
        )
        other_course = Course.objects.create(
            name="Databases",
            code="DB201",
            department=department,
            duration_years=1,
        )
        teacher.courses.add(allowed_course)

        student_one_user = user_model.objects.create_user(
            username="student_scope_one",
            password="test-password-123",
        )
        student_one = Student.objects.create(
            user=student_one_user,
            roll_number="CS201",
            department=department,
        )

        student_two_user = user_model.objects.create_user(
            username="student_scope_two",
            password="test-password-123",
        )
        student_two = Student.objects.create(
            user=student_two_user,
            roll_number="CS202",
            department=department,
        )

        allowed_enrollment = Enrollment.objects.create(
            student=student_one,
            course=allowed_course,
            academic_year="2026-2027",
        )
        other_enrollment = Enrollment.objects.create(
            student=student_two,
            course=other_course,
            academic_year="2026-2027",
        )

        form = AttendanceForm(teacher=teacher)
        allowed_ids = set(
            form.fields["enrollment"].queryset.values_list("id", flat=True)
        )

        self.assertIn(allowed_enrollment.id, allowed_ids)
        self.assertNotIn(other_enrollment.id, allowed_ids)



        allowed_assessment = Assessment.objects.create(
            course=allowed_course,
            title="Midterm",
            exam_date=date(2026, 11, 15),
            max_marks=Decimal("100"),
        )
        other_assessment = Assessment.objects.create(
            course=other_course,
            title="Other course exam",
            exam_date=date(2026, 11, 16),
            max_marks=Decimal("100"),
        )

        result_form = ResultForm(teacher=teacher)
        assessment_ids = set(
            result_form.fields["assessment"].queryset.values_list("id", flat=True)
        )

        self.assertIn(allowed_assessment.id, assessment_ids)
        self.assertNotIn(other_assessment.id, assessment_ids)

class NoticeFormScopeTests(TestCase):
    def test_teacher_only_sees_assigned_courses_in_notice_form(self):
        user_model = get_user_model()
        department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )

        teacher_user = user_model.objects.create_user(
            username="notice_teacher",
            password="test-password-123",
        )
        teacher = Teacher.objects.create(
            user=teacher_user,
            employee_id="T-NOTICE",
            department=department,
        )

        allowed_course = Course.objects.create(
            name="Python",
            code="PY401",
            department=department,
            duration_years=1,
        )
        other_course = Course.objects.create(
            name="Databases",
            code="DB401",
            department=department,
            duration_years=1,
        )
        teacher.courses.add(allowed_course)

        form = NoticeForm(teacher=teacher)
        course_ids = set(
            form.fields["course"].queryset.values_list("id", flat=True)
        )

        self.assertIn(allowed_course.id, course_ids)
        self.assertNotIn(other_course.id, course_ids)