from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from academics.models import Course, Department, Enrollment, Student, Teacher


class HomePageTests(TestCase):
    def test_home_page_returns_success(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_home_page_explains_project_purpose(self):
        response = self.client.get("/")

        self.assertContains(response, "College Management System")
        self.assertContains(response, "Milestone 1")

class TeacherStudentRosterTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        department = Department.objects.create(
            name="Computer Science",
            code="CS",
        )

        teacher_user = user_model.objects.create_user(
            username="roster_teacher",
            password="test-password-123",
        )
        teacher = Teacher.objects.create(
            user=teacher_user,
            employee_id="T-ROSTER",
            department=department,
        )

        allowed_course = Course.objects.create(
            name="Python",
            code="PY301",
            department=department,
            duration_years=1,
        )
        other_course = Course.objects.create(
            name="Databases",
            code="DB301",
            department=department,
            duration_years=1,
        )
        teacher.courses.add(allowed_course)

        allowed_user = user_model.objects.create_user(
            username="asha",
            password="test-password-123",
            first_name="Asha",
        )
        allowed_student = Student.objects.create(
            user=allowed_user,
            roll_number="CS301",
            department=department,
        )

        other_user = user_model.objects.create_user(
            username="ravi",
            password="test-password-123",
            first_name="Ravi",
        )
        other_student = Student.objects.create(
            user=other_user,
            roll_number="CS302",
            department=department,
        )

        Enrollment.objects.create(
            student=allowed_student,
            course=allowed_course,
            academic_year="2026-2027",
        )
        Enrollment.objects.create(
            student=other_student,
            course=other_course,
            academic_year="2026-2027",
        )

        self.client.force_login(teacher_user)

    def test_roster_is_scoped_and_searchable(self):
        response = self.client.get(reverse("teacher_students"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS301")
        self.assertNotContains(response, "CS302")

        response = self.client.get(
            reverse("teacher_students"),
            {"q": "Asha"},
        )
        self.assertContains(response, "CS301")
        self.assertNotContains(response, "CS302")
