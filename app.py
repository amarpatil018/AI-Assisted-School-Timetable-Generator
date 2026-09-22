from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "school.db"


# =========================================
# DATABASE CONNECTION
# =========================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =========================================
# CREATE DATABASE TABLES
# =========================================

def create_database():

    connection = get_db_connection()

    # Classes table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)

    # Teachers table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            subjects TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# =========================================
# SCHOOL SETTINGS
# =========================================

school_settings = {
    "school_name": "My School",
    "start_time": "08:30",
    "end_time": "15:30",
    "period_duration": 45,
    "number_of_periods": 8,
    "working_days": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ],
    "break_start": "12:30",
    "break_duration": 45
}


# =========================================
# DASHBOARD
# =========================================

@app.route("/")
def home():

    connection = get_db_connection()

    classes = connection.execute(
        "SELECT * FROM classes ORDER BY class_name, section"
    ).fetchall()

    teachers = connection.execute(
        "SELECT * FROM teachers ORDER BY teacher_name"
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        settings=school_settings,
        classes=classes,
        teachers=teachers
    )


# =========================================
# SCHOOL SETTINGS
# =========================================

@app.route("/settings", methods=["GET", "POST"])
def settings():

    if request.method == "POST":

        school_settings["school_name"] = request.form["school_name"]

        school_settings["start_time"] = request.form["start_time"]

        school_settings["end_time"] = request.form["end_time"]

        school_settings["period_duration"] = int(
            request.form["period_duration"]
        )

        school_settings["number_of_periods"] = int(
            request.form["number_of_periods"]
        )

        school_settings["working_days"] = request.form.getlist(
            "working_days"
        )

        school_settings["break_start"] = request.form["break_start"]

        school_settings["break_duration"] = int(
            request.form["break_duration"]
        )

        return redirect(url_for("settings"))

    return render_template(
        "settings.html",
        settings=school_settings
    )


# =========================================
# CLASSES
# =========================================

@app.route("/classes", methods=["GET", "POST"])
def classes():

    connection = get_db_connection()

    if request.method == "POST":

        class_name = request.form["class_name"].strip()
        section = request.form["section"].strip().upper()

        connection.execute(
            """
            INSERT INTO classes (class_name, section)
            VALUES (?, ?)
            """,
            (class_name, section)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("classes"))

    class_list = connection.execute(
        """
        SELECT * FROM classes
        ORDER BY class_name, section
        """
    ).fetchall()

    connection.close()

    return render_template(
        "classes.html",
        classes=class_list
    )


# =========================================
# DELETE CLASS
# =========================================

@app.route("/classes/delete/<int:class_id>")
def delete_class(class_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM classes WHERE id = ?",
        (class_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("classes"))


# =========================================
# TEACHERS
# =========================================

@app.route("/teachers", methods=["GET", "POST"])
def teachers():

    connection = get_db_connection()

    if request.method == "POST":

        teacher_name = request.form["teacher_name"].strip()

        subjects = request.form["subjects"].strip()

        connection.execute(
            """
            INSERT INTO teachers (teacher_name, subjects)
            VALUES (?, ?)
            """,
            (teacher_name, subjects)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("teachers"))

    teacher_list = connection.execute(
        """
        SELECT * FROM teachers
        ORDER BY teacher_name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "teachers.html",
        teachers=teacher_list
    )


# =========================================
# DELETE TEACHER
# =========================================

@app.route("/teachers/delete/<int:teacher_id>")
def delete_teacher(teacher_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM teachers WHERE id = ?",
        (teacher_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("teachers"))


# =========================================
# START APPLICATION
# =========================================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)