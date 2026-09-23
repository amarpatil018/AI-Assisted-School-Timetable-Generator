from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

app.secret_key = "smartschool-secret-key"

DATABASE = "school.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =========================================================
# SCHOOL SETTINGS
# =========================================================

school_settings = {
    "school_name": "AI-Assisted School Timetable Generator",
    "start_time": "09:00",
    "end_time": "16:00",
    "period_duration": 45,
    "number_of_periods": 7,
    "working_days": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ],
    "break_start": "12:00",
    "break_duration": 30
}


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            subjects TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            periods_per_week INTEGER NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            periods_per_week INTEGER NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def index():

    connection = get_db_connection()

    class_count = connection.execute(
        "SELECT COUNT(*) FROM classes"
    ).fetchone()[0]

    teacher_count = connection.execute(
        "SELECT COUNT(*) FROM teachers"
    ).fetchone()[0]

    subject_count = connection.execute(
        "SELECT COUNT(*) FROM subjects"
    ).fetchone()[0]

    assignment_count = connection.execute(
        "SELECT COUNT(*) FROM assignments"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        class_count=class_count,
        teacher_count=teacher_count,
        subject_count=subject_count,
        assignment_count=assignment_count,
        school_settings=school_settings
    )


# Allow templates using url_for('home')
app.add_url_rule(
    "/",
    endpoint="home",
    view_func=index
)


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings", methods=["GET", "POST"])
def settings():

    if request.method == "POST":

        school_settings["school_name"] = request.form.get(
            "school_name",
            "AI-Assisted School Timetable Generator"
        )

        school_settings["start_time"] = request.form.get(
            "start_time",
            "09:00"
        )

        school_settings["end_time"] = request.form.get(
            "end_time",
            "16:00"
        )

        try:
            school_settings["period_duration"] = int(
                request.form.get("period_duration", 45)
            )
        except ValueError:
            school_settings["period_duration"] = 45

        try:
            school_settings["number_of_periods"] = int(
                request.form.get("number_of_periods", 7)
            )
        except ValueError:
            school_settings["number_of_periods"] = 7

        school_settings["break_start"] = request.form.get(
            "break_start",
            "12:00"
        )

        try:
            school_settings["break_duration"] = int(
                request.form.get("break_duration", 30)
            )
        except ValueError:
            school_settings["break_duration"] = 30

        working_days = request.form.getlist("working_days")

        if working_days:
            school_settings["working_days"] = working_days

        return redirect(url_for("settings"))

    return render_template(
        "settings.html",
        school_settings=school_settings
    )


# =========================================================
# CLASSES
# =========================================================

@app.route("/classes", methods=["GET", "POST"])
def classes():

    connection = get_db_connection()

    if request.method == "POST":

        class_name = request.form.get(
            "class_name",
            ""
        ).strip()

        section = request.form.get(
            "section",
            ""
        ).strip()

        if class_name and section:

            connection.execute(
                """
                INSERT INTO classes
                (class_name, section)
                VALUES (?, ?)
                """,
                (class_name, section)
            )

            connection.commit()

        connection.close()

        return redirect(url_for("classes"))

    class_list = connection.execute(
        """
        SELECT *
        FROM classes
        ORDER BY class_name, section
        """
    ).fetchall()

    connection.close()

    return render_template(
        "classes.html",
        classes=class_list
    )


# =========================================================
# DELETE CLASS
# =========================================================
# IMPORTANT:
# Template uses class_id, so the route also uses class_id.

@app.route("/classes/delete/<int:class_id>")
def delete_class(class_id):

    connection = get_db_connection()

    # Delete related assignments first
    connection.execute(
        "DELETE FROM assignments WHERE class_id = ?",
        (class_id,)
    )

    connection.execute(
        "DELETE FROM classes WHERE id = ?",
        (class_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("classes"))


# =========================================================
# TEACHERS
# =========================================================

@app.route("/teachers", methods=["GET", "POST"])
def teachers():

    connection = get_db_connection()

    if request.method == "POST":

        teacher_name = request.form.get(
            "teacher_name",
            ""
        ).strip()

        subjects = request.form.get(
            "subjects",
            ""
        ).strip()

        if teacher_name:

            connection.execute(
                """
                INSERT INTO teachers
                (teacher_name, subjects)
                VALUES (?, ?)
                """,
                (teacher_name, subjects)
            )

            connection.commit()

        connection.close()

        return redirect(url_for("teachers"))

    teacher_list = connection.execute(
        """
        SELECT *
        FROM teachers
        ORDER BY teacher_name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "teachers.html",
        teachers=teacher_list
    )


# =========================================================
# DELETE TEACHER
# =========================================================

@app.route("/teachers/delete/<int:teacher_id>")
def delete_teacher(teacher_id):

    connection = get_db_connection()

    # Delete related assignments first
    connection.execute(
        "DELETE FROM assignments WHERE teacher_id = ?",
        (teacher_id,)
    )

    connection.execute(
        "DELETE FROM teachers WHERE id = ?",
        (teacher_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("teachers"))


# =========================================================
# SUBJECTS
# =========================================================

@app.route("/subjects", methods=["GET", "POST"])
def subjects():

    connection = get_db_connection()

    if request.method == "POST":

        subject_name = request.form.get(
            "subject_name",
            ""
        ).strip()

        try:
            periods_per_week = int(
                request.form.get(
                    "periods_per_week",
                    1
                )
            )
        except ValueError:
            periods_per_week = 1

        if subject_name and periods_per_week > 0:

            connection.execute(
                """
                INSERT INTO subjects
                (subject_name, periods_per_week)
                VALUES (?, ?)
                """,
                (
                    subject_name,
                    periods_per_week
                )
            )

            connection.commit()

        connection.close()

        return redirect(url_for("subjects"))

    subject_list = connection.execute(
        """
        SELECT *
        FROM subjects
        ORDER BY subject_name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "subjects.html",
        subjects=subject_list
    )


# =========================================================
# DELETE SUBJECT
# =========================================================

@app.route("/subjects/delete/<int:subject_id>")
def delete_subject(subject_id):

    connection = get_db_connection()

    # Delete related assignments first
    connection.execute(
        "DELETE FROM assignments WHERE subject_id = ?",
        (subject_id,)
    )

    connection.execute(
        "DELETE FROM subjects WHERE id = ?",
        (subject_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("subjects"))


# =========================================================
# ASSIGNMENTS
# =========================================================

@app.route("/assignments", methods=["GET", "POST"])
def assignments():

    connection = get_db_connection()

    if request.method == "POST":

        class_id = request.form.get("class_id")
        subject_id = request.form.get("subject_id")
        teacher_id = request.form.get("teacher_id")

        try:
            periods_per_week = int(
                request.form.get(
                    "periods_per_week",
                    1
                )
            )
        except ValueError:
            periods_per_week = 1

        if (
            class_id
            and subject_id
            and teacher_id
            and periods_per_week > 0
        ):

            # Prevent exact duplicate assignment
            existing = connection.execute(
                """
                SELECT id
                FROM assignments
                WHERE class_id = ?
                AND subject_id = ?
                AND teacher_id = ?
                """,
                (
                    class_id,
                    subject_id,
                    teacher_id
                )
            ).fetchone()

            if not existing:

                connection.execute(
                    """
                    INSERT INTO assignments
                    (
                        class_id,
                        subject_id,
                        teacher_id,
                        periods_per_week
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        class_id,
                        subject_id,
                        teacher_id,
                        periods_per_week
                    )
                )

                connection.commit()

        connection.close()

        return redirect(url_for("assignments"))

    class_list = connection.execute(
        """
        SELECT *
        FROM classes
        ORDER BY class_name, section
        """
    ).fetchall()

    teacher_list = connection.execute(
        """
        SELECT *
        FROM teachers
        ORDER BY teacher_name
        """
    ).fetchall()

    subject_list = connection.execute(
        """
        SELECT *
        FROM subjects
        ORDER BY subject_name
        """
    ).fetchall()

    assignment_list = connection.execute(
        """
        SELECT
            assignments.id,
            assignments.periods_per_week,

            classes.class_name,
            classes.section,

            subjects.subject_name,

            teachers.teacher_name

        FROM assignments

        JOIN classes
            ON assignments.class_id = classes.id

        JOIN subjects
            ON assignments.subject_id = subjects.id

        JOIN teachers
            ON assignments.teacher_id = teachers.id

        ORDER BY
            classes.class_name,
            classes.section,
            subjects.subject_name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "assignments.html",
        classes=class_list,
        teachers=teacher_list,
        subjects=subject_list,
        assignments=assignment_list
    )


# =========================================================
# DELETE ASSIGNMENT
# =========================================================

@app.route("/assignments/delete/<int:assignment_id>")
def delete_assignment(assignment_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM assignments WHERE id = ?",
        (assignment_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("assignments"))


# =========================================================
# AUTOMATIC TIMETABLE GENERATOR
# =========================================================

@app.route("/generate-timetable")
def generate_timetable():

    connection = get_db_connection()

    assignments = connection.execute(
        """
        SELECT
            assignments.class_id,
            assignments.subject_id,
            assignments.teacher_id,
            assignments.periods_per_week,

            classes.class_name,
            classes.section,

            subjects.subject_name,

            teachers.teacher_name

        FROM assignments

        JOIN classes
            ON assignments.class_id = classes.id

        JOIN subjects
            ON assignments.subject_id = subjects.id

        JOIN teachers
            ON assignments.teacher_id = teachers.id
        """
    ).fetchall()

    connection.close()

    # -----------------------------------------------------
    # NO ASSIGNMENTS
    # -----------------------------------------------------

    if not assignments:

        return render_template(
            "timetable.html",
            timetable={},
            days=school_settings["working_days"],
            number_of_periods=school_settings["number_of_periods"],
            class_information={},
            unscheduled=[],
            error=(
                "No assignments found. "
                "Please add teacher assignments first."
            )
        )

    days = school_settings["working_days"]

    number_of_periods = school_settings[
        "number_of_periods"
    ]

    # -----------------------------------------------------
    # VALIDATE SETTINGS
    # -----------------------------------------------------

    if not days:

        return render_template(
            "timetable.html",
            timetable={},
            days=[],
            number_of_periods=number_of_periods,
            class_information={},
            unscheduled=[],
            error=(
                "No working days are configured. "
                "Please configure working days in Settings."
            )
        )

    if number_of_periods <= 0:

        return render_template(
            "timetable.html",
            timetable={},
            days=days,
            number_of_periods=number_of_periods,
            class_information={},
            unscheduled=[],
            error=(
                "The number of periods must be greater than zero."
            )
        )

    # -----------------------------------------------------
    # CREATE EMPTY TIMETABLE
    # -----------------------------------------------------

    timetable = {}

    for assignment in assignments:

        class_id = assignment["class_id"]

        if class_id not in timetable:

            timetable[class_id] = {}

            for day in days:

                timetable[class_id][day] = {}

                for period in range(
                    1,
                    number_of_periods + 1
                ):

                    timetable[class_id][day][period] = None

    # -----------------------------------------------------
    # TRACK TEACHER OCCUPANCY
    # -----------------------------------------------------

    teacher_busy = set()

    # -----------------------------------------------------
    # CREATE INDIVIDUAL LESSONS
    # -----------------------------------------------------

    lessons = []

    for assignment in assignments:

        try:
            periods = int(
                assignment["periods_per_week"]
            )
        except (ValueError, TypeError):
            periods = 1

        if periods < 1:
            periods = 1

        for _ in range(periods):

            lessons.append({
                "class_id": assignment["class_id"],
                "subject_id": assignment["subject_id"],
                "teacher_id": assignment["teacher_id"],
                "class_name": assignment["class_name"],
                "section": assignment["section"],
                "subject_name": assignment["subject_name"],
                "teacher_name": assignment["teacher_name"]
            })

    random.shuffle(lessons)

    # -----------------------------------------------------
    # SCHEDULE LESSONS
    # -----------------------------------------------------

    unscheduled_lessons = []

    for lesson in lessons:

        possible_slots = []

        class_id = lesson["class_id"]
        teacher_id = lesson["teacher_id"]

        for day in days:

            for period in range(
                1,
                number_of_periods + 1
            ):

                # Class already has a lesson
                if timetable[class_id][day][period] is not None:
                    continue

                # Teacher already teaching somewhere else
                teacher_slot = (
                    teacher_id,
                    day,
                    period
                )

                if teacher_slot in teacher_busy:
                    continue

                possible_slots.append(
                    (day, period)
                )

        # -------------------------------------------------
        # PLACE LESSON
        # -------------------------------------------------

        if possible_slots:

            day, period = random.choice(
                possible_slots
            )

            timetable[class_id][day][period] = lesson

            teacher_busy.add(
                (
                    teacher_id,
                    day,
                    period
                )
            )

        else:

            unscheduled_lessons.append(
                lesson
            )

    # -----------------------------------------------------
    # CLASS INFORMATION
    # -----------------------------------------------------

    class_information = {}

    for assignment in assignments:

        class_id = assignment["class_id"]

        class_information[class_id] = {
            "class_name": assignment["class_name"],
            "section": assignment["section"]
        }

    # -----------------------------------------------------
    # DISPLAY TIMETABLE
    # -----------------------------------------------------

    return render_template(
        "timetable.html",
        timetable=timetable,
        days=days,
        number_of_periods=number_of_periods,
        class_information=class_information,
        unscheduled=unscheduled_lessons,
        error=None
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    initialize_database()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )