# College Management System

A Django website for keeping college academic records in one place. Staff manage the data, teachers work with their assigned courses, and students see information linked to their own enrollment.

## What the project does

- Stores departments, courses, students, teachers, enrollments, attendance, assessments, results, assignments, and notices.
- Gives teachers and students role-specific dashboards after sign-in.
- Lets teachers search and paginate their course rosters.
- Lets teachers record attendance and assessment results for their assigned courses.
- Lets teachers post course assignments and notices.
- Restricts assignment downloads to students enrolled in that course.
- Uses Django forms, validation, database constraints, and the Django ORM to protect and manage records.

## How the website works

~~~mermaid
flowchart TD
    A[Staff adds academic records in Django Admin] --> DB[(College database)]
    T[Teacher] --> L[Sign in]
    S[Student] --> L
    L --> V{Does the user have a linked role profile?}
    V -->|Teacher| TD[Teacher dashboard]
    V -->|Student| SD[Student dashboard]
    V -->|No profile| X[Show access denied]

    TD --> C[Teacher's assigned courses]
    C --> R[Search or page through student roster]
    C --> AT[Mark attendance]
    C --> RS[Enter assessment results]
    C --> AS[Post assignments]
    C --> N[Post notices]

    SD --> E[Student's own enrollments]
    E --> O[View own courses, attendance, and results]
    E --> CN[Read course assignments and notices]
    CN --> D{Enrolled in this course?}
    D -->|Yes| F[Download assignment]
    D -->|No| X

    R --> ORM[Django validation and ORM]
    AT --> ORM
    RS --> ORM
    AS --> ORM
    N --> ORM
    ORM --> DB
    DB --> TD
    DB --> SD
~~~

**In short:** Django checks who signed in, shows the correct dashboard, validates each change, and saves it to the database. Students only see their own academic information, and assignment downloads are checked against course enrollment.

## Main data relationships

~~~
Department ──< Course
Department ──< Student >── User
Department ──< Teacher >── User
Teacher >──< Course
Student ──< Enrollment >── Course
Enrollment ──< Attendance
Course ──< Assessment
Enrollment ──< Result >── Assessment
Course ──< Assignment >── Teacher
Course ──< Notice >── Teacher
~~~

## Technology

- Python 3.13
- Django 6.0.4
- SQLite for local development
- python-dotenv for local settings
- Django templates, HTML, and CSS

## Run it on Windows

Open PowerShell in the folder where you cloned this repository.

### 1. Create a virtual environment and install the packages

~~~
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

### 2. Create your private local settings file

~~~
Copy-Item .env.example .env
~~~

Open .env and replace the example secret with a random key. To generate one, run:

~~~
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
~~~

Copy the printed key into DJANGO_SECRET_KEY in .env. Keep .env private; Git ignores it.

### 3. Create the database and administrator account

~~~
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
~~~

### 4. Start Django

~~~
.\.venv\Scripts\python.exe manage.py runserver
~~~

Visit http://127.0.0.1:8000/ for the website or http://127.0.0.1:8000/admin/ for the admin area. Add departments, courses, user accounts, and student or teacher profiles through Django Admin before testing the role dashboards.

## Run the automated checks

~~~
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
~~~

## Project files

~~~
academics/      Models, forms, validation, and migrations for college records
config/         Django settings and URL configuration
core/           Pages, dashboards, templates, and CSS
manage.py       Django command-line entry point
requirements.txt
.env.example    Safe template for local settings
README.md       Project guide and flowchart
LICENSE
~~~

## Local files and security

The repository does not include a working database, uploaded files, secrets, virtual environments, or Python cache files. These are created locally and excluded by .gitignore.

This is a learning project for local use. Before deploying it publicly, configure production secrets, HTTPS, a production database, and secure file storage. The Django development server is only for local development.

## Current limits and future work

Possible next improvements include a production deployment, a dedicated reporting page, timetable management, email notifications, and OCR for scanned assignment PDFs.
