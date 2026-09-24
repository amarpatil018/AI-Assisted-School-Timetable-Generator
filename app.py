from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
import os


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = "smart-school-timetable-secret-key"


# =========================================================
# DATABASE
# =========================================================

DATABASE = "school.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


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
            periods_per_week INTEGER NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# SCHOOL SETTINGS
# =========================================================

school_settings = {

    "school_name": "My School",

    "start_time": "09:00",

    "end_time": "16:00",

    "period_duration": 45,

    "number_of_periods": 8,

    "working_days": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ],

    "break_start": "12:30",

    "break_duration": 30
}


# =========================================================
# HOME / DASHBOARD
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
        settings=school_settings
    )


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings", methods=["GET", "POST"])
def settings():

    global school_settings

    if request.method == "POST":

        school_name = request.form.get(
            "school_name",
            "My School"
        ).strip()

        start_time = request.form.get(
            "start_time",
            "09:00"
        )

        end_time = request.form.get(
            "end_time",
            "16:00"
        )

        period_duration = request.form.get(
            "period_duration",
            "45"
        )

        number_of_periods = request.form.get(
            "number_of_periods",
            "8"
        )

        break_start = request.form.get(
            "break_start",
            "12:30"
        )

        break_duration = request.form.get(
            "break_duration",
            "30"
        )

        try:
            period_duration = int(period_duration)
        except ValueError:
            period_duration = 45

        try:
            number_of_periods = int(number_of_periods)
        except ValueError:
            number_of_periods = 8

        try:
            break_duration = int(break_duration)
        except ValueError:
            break_duration = 30

        working_days = request.form.getlist(
            "working_days"
        )

        if not working_days:
            working_days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday"
            ]

        school_settings = {

            "school_name": school_name,

            "start_time": start_time,

            "end_time": end_time,

            "period_duration": period_duration,

            "number_of_periods": number_of_periods,

            "working_days": working_days,

            "break_start": break_start,

            "break_duration": break_duration
        }

        return redirect(url_for("settings"))

    return render_template(
        "settings.html",
        settings=school_settings
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


@app.route("/classes/delete/<int:class_id>")
def delete_class(class_id):

    connection = get_db_connection()

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


@app.route("/teachers/delete/<int:teacher_id>")
def delete_teacher(teacher_id):

    connection = get_db_connection()

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

        periods_per_week = request.form.get(
            "periods_per_week",
            "5"
        )

        try:
            periods_per_week = int(periods_per_week)
        except ValueError:
            periods_per_week = 5

        if subject_name and periods_per_week > 0:

            connection.execute(
                """
                INSERT INTO subjects
                (subject_name, periods_per_week)
                VALUES (?, ?)
                """,
                (subject_name, periods_per_week)
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


@app.route("/subjects/delete/<int:subject_id>")
def delete_subject(subject_id):

    connection = get_db_connection()

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

        periods_per_week = request.form.get(
            "periods_per_week",
            "1"
        )

        try:
            class_id = int(class_id)
            subject_id = int(subject_id)
            teacher_id = int(teacher_id)
            periods_per_week = int(periods_per_week)
        except (ValueError, TypeError):
            connection.close()
            return redirect(url_for("assignments"))

        if periods_per_week < 1:
            periods_per_week = 1

        # Prevent duplicate assignment
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

        if existing:

            connection.execute(
                """
                UPDATE assignments
                SET periods_per_week = ?
                WHERE id = ?
                """,
                (
                    periods_per_week,
                    existing["id"]
                )
            )

        else:

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
# TIMETABLE GENERATOR
# =========================================================

@app.route("/generate-timetable")
def generate_timetable():

    connection = get_db_connection()

    assignments = connection.execute(
        """
        SELECT

            assignments.id AS assignment_id,

            assignments.class_id,

            assignments.subject_id,

            assignments.teacher_id,

            assignments.periods_per_week,

            classes.class_name,

            classes.section,

            subjects.subject_name,

            subjects.periods_per_week AS subject_periods,

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

    days = school_settings["working_days"]

    number_of_periods = school_settings[
        "number_of_periods"
    ]

    # -----------------------------------------------------
    # No assignments
    # -----------------------------------------------------

    if not assignments:

        return render_template(
            "timetable.html",

            timetable={},

            days=days,

            number_of_periods=number_of_periods,

            class_information={},

            unscheduled=[],

            error=(
                "No assignments found. "
                "Please add teacher assignments first."
            )
        )

    # -----------------------------------------------------
    # Create timetable structure
    # -----------------------------------------------------

    class_ids = sorted(
        set(
            assignment["class_id"]
            for assignment in assignments
        )
    )

    timetable = {}

    for class_id in class_ids:

        timetable[class_id] = {}

        for day in days:

            timetable[class_id][day] = {}

            for period in range(
                1,
                number_of_periods + 1
            ):

                timetable[class_id][day][period] = None

    # -----------------------------------------------------
    # Teacher busy tracking
    # -----------------------------------------------------

    teacher_busy = set()

    # -----------------------------------------------------
    # Create individual lessons
    # -----------------------------------------------------

    lessons = []

    for assignment in assignments:

        periods = assignment["periods_per_week"]

        for lesson_number in range(periods):

            lessons.append({

                "assignment_id":
                    assignment["assignment_id"],

                "class_id":
                    assignment["class_id"],

                "subject_id":
                    assignment["subject_id"],

                "teacher_id":
                    assignment["teacher_id"],

                "class_name":
                    assignment["class_name"],

                "section":
                    assignment["section"],

                "subject_name":
                    assignment["subject_name"],

                "teacher_name":
                    assignment["teacher_name"]
            })

    # -----------------------------------------------------
    # Randomize
    # -----------------------------------------------------

    random.shuffle(lessons)

    unscheduled_lessons = []

    # -----------------------------------------------------
    # Schedule lessons
    # -----------------------------------------------------

    for lesson in lessons:

        possible_slots = []

        for day in days:

            for period in range(
                1,
                number_of_periods + 1
            ):

                # Class already occupied
                if timetable[
                    lesson["class_id"]
                ][day][period] is not None:

                    continue

                # Teacher already occupied
                teacher_slot = (
                    lesson["teacher_id"],
                    day,
                    period
                )

                if teacher_slot in teacher_busy:

                    continue

                possible_slots.append(
                    (day, period)
                )

        # -------------------------------------------------
        # Assign lesson
        # -------------------------------------------------

        if possible_slots:

            day, period = random.choice(
                possible_slots
            )

            timetable[
                lesson["class_id"]
            ][day][period] = lesson

            teacher_busy.add(
                (
                    lesson["teacher_id"],
                    day,
                    period
                )
            )

        else:

            unscheduled_lessons.append(
                lesson
            )

    # -----------------------------------------------------
    # Class information
    # -----------------------------------------------------

    class_information = {}

    for assignment in assignments:

        class_information[
            assignment["class_id"]
        ] = {

            "class_name":
                assignment["class_name"],

            "section":
                assignment["section"]
        }

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
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    initialize_database()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )