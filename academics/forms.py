from django import forms
from .models import (
    Assessment,
    Assignment,
    Attendance,
    Course,
    Enrollment,
    Result,
    Notice,
)


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ("enrollment", "attendance_date", "status", "remarks")
        widgets = {
            "attendance_date": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)

        if teacher is None:
            self.fields["enrollment"].queryset = Enrollment.objects.none()
        else:
            self.fields["enrollment"].queryset = (
                Enrollment.objects
                .filter(course__teachers=teacher)
                .select_related("student__user", "course")
                .distinct()
            )

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = (
            "enrollment",
            "assessment",
            "marks_obtained",
            "remarks",
        )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)

        if teacher is None:
            self.fields["enrollment"].queryset = Enrollment.objects.none()
            self.fields["assessment"].queryset = Assessment.objects.none()
        else:
            self.fields["enrollment"].queryset = (
                Enrollment.objects
                .filter(course__teachers=teacher)
                .select_related("student__user", "course")
                .distinct()
            )
            self.fields["assessment"].queryset = (
                Assessment.objects
                .filter(course__teachers=teacher)
                .select_related("course")
                .distinct()
            )

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ("course", "title", "description", "file", "due_date")
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)

        if teacher is None:
            self.fields["course"].queryset = Course.objects.none()
        else:
            self.fields["course"].queryset = teacher.courses.all()

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ("course", "title", "message", "important")
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)

        if teacher is None:
            self.fields["course"].queryset = Course.objects.none()
        else:
            self.fields["course"].queryset = teacher.courses.all()