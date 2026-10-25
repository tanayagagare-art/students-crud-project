# Students CRUD API

A beginner-friendly Python backend project for managing student records with FastAPI and SQLite.

## Features

- Create, read, update, and delete student records (CRUD)
- Automatically creates `students.db` and the `students` table on startup
- Validates names, dates, email addresses, and contact information
- Filter students by name, course, or date of birth
- Returns `404` when a requested student does not exist
- Interactive API documentation at `/docs`

## Requirements

- Python 3.10 or newer (Python 3.11+ recommended)
- Internet connection for installing dependencies

## Install and run

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

If PowerShell blocks activation, you can run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs in your browser to test the API.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/students` | Create a student |
| `GET` | `/students` | List all students |
| `GET` | `/students/{student_id}` | Get one student |
| `PUT` | `/students/{student_id}` | Replace all editable student details |
| `PATCH` | `/students/{student_id}` | Update only provided fields |
| `DELETE` | `/students/{student_id}` | Delete a student |

### Example request body

Use this JSON with `POST /students`:

```json
{
  "name": "Rahul Patil",
  "date_of_birth": "2005-05-15",
  "email": "rahul@example.com",
  "phone": "9876543210",
  "course": "Python Backend",
  "address": "Pune, Maharashtra",
  "enrollment_date": "2026-10-01"
}
```

`student_id` is generated automatically. Provide at least one of `email` or `phone`.

### Filtering examples

- `GET /students?name=Rahul`
- `GET /students?course=Python`
- `GET /students?born_after=2005-01-01`

## Suggested testing flow

1. Run the app and open `/docs`.
2. Expand `POST /students`, choose **Try it out**, paste the example JSON, then choose **Execute**.
3. Use `GET /students` to confirm the record was saved.
4. Use `GET /students/{student_id}` to fetch one record.
5. Use `PATCH /students/{student_id}` to change one field, e.g. `{"course": "FastAPI"}`.
6. Use `PUT /students/{student_id}` to replace all editable details.
7. Use `DELETE /students/{student_id}` to delete the record.
8. Try an ID that does not exist and confirm the API returns `404`.

## Project structure

```text
students_crud_project/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Database and privacy

The SQLite database file is created locally when the app first starts. Do not commit the database file or real student personal information to GitHub. Use fictional data for demos.

## Notes

This project implements the required FastAPI + SQLite CRUD core. The optional Ollama AI feature is not included; finish and test the core application first.
