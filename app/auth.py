"""
student course registration system
auth.py — login and registration logic for students and admins
"""

from app.db_connection import get_connection


def register_student(name, email, password, semester):
    """registers a new student. returns (success: bool, message: str)"""
    conn = get_connection()
    if not conn:
        return False, "database connection failed."
    try:
        cursor = conn.cursor()
        cursor.execute(
            "insert into student (name, email, password, semester) values (%s, %s, %s, %s)",
            (name, email, password, semester)
        )
        conn.commit()
        return True, "registration successful."
    except Exception as e:
        if "duplicate" in str(e).lower():
            return False, "email already registered."
        return False, f"error: {e}"
    finally:
        conn.close()


def login_student(email, password):
    """returns student row dict if credentials match, else None"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "select * from student where email=%s and password=%s",
            (email, password)
        )
        return cursor.fetchone()
    finally:
        conn.close()


def login_admin(email, password):
    """returns admin row dict if credentials match, else None"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "select * from admin where email=%s and password=%s",
            (email, password)
        )
        return cursor.fetchone()
    finally:
        conn.close()
