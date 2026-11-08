from pathlib import Path

from django.core.exceptions import ValidationError


MAX_ASSIGNMENT_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_assignment_pdf(uploaded_file):
    if uploaded_file.size > MAX_ASSIGNMENT_SIZE:
        raise ValidationError("PDF file 5 MB se chhoti honi chahiye.")

    if Path(uploaded_file.name).suffix.lower() != ".pdf":
        raise ValidationError("Sirf PDF file upload kar sakte ho.")

    uploaded_file.seek(0)
    file_header = uploaded_file.read(5)
    uploaded_file.seek(0)

    if file_header != b"%PDF-":
        raise ValidationError("Yeh valid PDF file nahi lagti.")