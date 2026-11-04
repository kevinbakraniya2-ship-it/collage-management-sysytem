from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from .validators import validate_assignment_pdf


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=12, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="courses",
    )
    duration_years = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="student_profile",
    )
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="students",
    )
    admission_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["roll_number"]

    def __str__(self):
        student_name = self.user.get_full_name() or self.user.username
        return f"{self.roll_number} — {student_name}"

class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="teacher_profile",
    )
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="teachers",
    )
    courses = models.ManyToManyField(
        Course,
        blank=True,
        related_name="teachers",
    )
    joining_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["employee_id"]

    def __str__(self):
        teacher_name = self.user.get_full_name() or self.user.username
        return f"{self.employee_id} — {teacher_name}"

class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        WITHDRAWN = "withdrawn", "Withdrawn"

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )
    academic_year = models.CharField(
        max_length=9,
        help_text="Example: 2026-2027",
    )
    enrolled_on = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["academic_year", "student__roll_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course", "academic_year"],
                name="unique_student_course_year",
            )
        ]

    def __str__(self):
        return (
            f"{self.student.roll_number} — {self.course.code} "
            f"({self.academic_year})"
        )

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )
    attendance_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
    )
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-attendance_date", "enrollment"]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "attendance_date"],
                name="uniq_attendance_enroll_day",
            )
        ]

    def __str__(self):
        return (
            f"{self.enrollment} — "
            f"{self.attendance_date}: {self.get_status_display()}"
        )

class Assessment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="assessments",
    )
    title = models.CharField(max_length=100)
    exam_date = models.DateField()
    max_marks = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["-exam_date", "title"]

    def __str__(self):
        return f"{self.title} — {self.course.code}"


class Result(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.PROTECT,
        related_name="results",
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.PROTECT,
        related_name="results",
    )
    marks_obtained = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    remarks = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "assessment"],
                name="uniq_result_enrollment_exam",
            )
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.enrollment_id and self.assessment_id:
            if self.enrollment.course_id != self.assessment.course_id:
                raise ValidationError({
                    "assessment": "Assessment must belong to the student's enrolled course."
                })

            if (
                self.marks_obtained is not None
                and self.marks_obtained > self.assessment.max_marks
            ):
                raise ValidationError({
                    "marks_obtained": "Marks cannot be greater than the assessment maximum."
                })

    def __str__(self):
        return f"{self.enrollment.student.roll_number} — {self.assessment}"


class Assignment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to="assignments/%Y/%m/",
        validators=[validate_assignment_pdf],
    )
    due_date = models.DateField()
    posted_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "title"]

    def clean(self):
        if (
            self.teacher_id
            and self.course_id
            and not self.teacher.courses.filter(pk=self.course_id).exists()
        ):
            raise ValidationError({
                "course": "Tum sirf apne assigned Course mein assignment de sakte ho."
            })

    def __str__(self):
        return f"{self.title} — {self.course.code}"

class Notice(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="notices",
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name="notices",
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    important = models.BooleanField(default=False)

    class Meta:
        ordering = ["-posted_on"]

    def clean(self):
        if (
            self.teacher_id
            and self.course_id
            and not self.teacher.courses.filter(pk=self.course_id).exists()
        ):
            raise ValidationError({
                "course": "Tum sirf apne assigned Course ke liye Notice post kar sakte ho."
            })

    def __str__(self):
        return f"{self.title} — {self.course.code}"