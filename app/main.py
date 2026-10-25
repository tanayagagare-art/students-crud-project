from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status

from app.database import get_connection, init_db
from app.schemas import StudentCreate, StudentResponse, StudentUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Students CRUD API",
    description="Internship project: manage student records using FastAPI and SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


def row_to_dict(row):
    return dict(row) if row is not None else None


@app.get("/", tags=["Home"])
def home():
    return {
        "message": "Students CRUD API is running",
        "docs": "/docs",
        "endpoints": {
            "create": "POST /students",
            "list": "GET /students",
            "get_one": "GET /students/{student_id}",
            "update": "PUT/PATCH /students/{student_id}",
            "delete": "DELETE /students/{student_id}",
        },
    }


@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentCreate):
    data = student.model_dump(mode="json")
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO students
                (name, date_of_birth, email, phone, course, address, enrollment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["date_of_birth"],
                data["email"],
                data["phone"],
                data["course"],
                data["address"],
                data["enrollment_date"],
            ),
        )
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (cursor.lastrowid,)
        ).fetchone()
    return row_to_dict(row)


@app.get("/students", response_model=list[StudentResponse], tags=["Students"])
def list_students(
    name: Optional[str] = Query(default=None, description="Filter by part of a student's name"),
    course: Optional[str] = Query(default=None, description="Filter by course"),
    born_after: Optional[date] = Query(default=None, description="Only students born after this date"),
):
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if course:
        query += " AND course LIKE ?"
        params.append(f"%{course}%")
    if born_after:
        query += " AND date_of_birth > ?"
        params.append(born_after.isoformat())

    query += " ORDER BY student_id"
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [row_to_dict(row) for row in rows]


@app.get("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def get_student(student_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return row_to_dict(row)


@app.put("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def replace_student(student_id: int, student: StudentCreate):
    data = student.model_dump(mode="json")
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT student_id FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Student not found")

        connection.execute(
            """
            UPDATE students
            SET name = ?, date_of_birth = ?, email = ?, phone = ?,
                course = ?, address = ?, enrollment_date = ?
            WHERE student_id = ?
            """,
            (
                data["name"], data["date_of_birth"], data["email"], data["phone"],
                data["course"], data["address"], data["enrollment_date"], student_id,
            ),
        )
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
    return row_to_dict(row)


@app.patch("/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def update_student(student_id: int, student: StudentUpdate):
    changes = student.model_dump(exclude_unset=True, mode="json")
    if not changes:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    allowed_fields = {
        "name", "date_of_birth", "email", "phone", "course", "address", "enrollment_date"
    }
    if not set(changes).issubset(allowed_fields):
        raise HTTPException(status_code=400, detail="Invalid fields")

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Student not found")

        merged = dict(existing)
        merged.update(changes)
        if not merged.get("email") and not merged.get("phone"):
            raise HTTPException(status_code=422, detail="A student must have an email or phone number")

        assignments = ", ".join(f"{field} = ?" for field in changes)
        values = [
            value.isoformat() if isinstance(value, date) else value
            for value in changes.values()
        ]
        with connection:
            connection.execute(
                f"UPDATE students SET {assignments} WHERE student_id = ?",
                (*values, student_id),
            )
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
    return row_to_dict(row)


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(student_id: int):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM students WHERE student_id = ?", (student_id,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
