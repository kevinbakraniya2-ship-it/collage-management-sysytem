# College Management System

A beginner-friendly Django project for a college. We build one verified feature at a time and explain the code as we go.

## Current milestone

Milestone 1 provides secure environment-based settings, a starter home page, and a smoke test. The feature apps for accounts, academics, attendance, and assessments will be added in later milestones.

## Run locally on Windows PowerShell

1. Create a virtual environment. Calling its Python directly avoids PowerShell activation-policy problems:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Create the local settings file and a random secret key:

   ```powershell
   Copy-Item .env.example .env
   .\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Open `.env` and replace the example value for `DJANGO_SECRET_KEY` with the generated value. Keep `.env` private; it is ignored by Git.

3. Check the project and start the local server:

   ```powershell
   .\.venv\Scripts\python.exe manage.py check
   .\.venv\Scripts\python.exe manage.py test
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py runserver
   ```

4. Visit `http://127.0.0.1:8000/`.

## Safety notes

- Never commit `.env`, database files, passwords, or private keys.
- `DJANGO_DEBUG=True` is for local learning only. Production settings require HTTPS and secure cookies.
- SQLite is for local development; production database and deployment are later topics.
