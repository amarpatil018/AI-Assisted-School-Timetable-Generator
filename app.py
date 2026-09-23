from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "smartschool-secret-key"

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
            subjects TEXT NOT NULL
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

            FOREIGN KEY (class_id)
                REFERENCES classes(id),

            FOREIGN KEY (subject_id)
                REFERENCES subjects(id),

            FOREIGN KEY (teacher_id)
                REFERENCES teachers(id)
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

    classes = connection.execute("""
        SELECT *
        FROM classes
        ORDER BY class_name, section
    """).fetchall()

    teachers = connection.execute("""
        SELECT *
        FROM teachers
        ORDER BY teacher_name
    """).fetchall()

    subjects = connection.execute("""
        SELECT *
        FROM subjects
        ORDER BY subject_name
    """).fetchall()

    assignments = connection.execute("""
        SELECT *
        FROM assignments
    """).fetchall()

    connection.close()

    return render_template(
        "index.html",
        settings=school_settings,
        classes=classes,
        teachers=teachers,
        subjects=subjects,
        assignments=assignments
    )


# =========================================
# SCHOOL SETTINGS
# =========================================

@app.route("/settings", methods=["GET", "POST"])
def settings():

    if request.method == "POST":

        school_settings["school_name"] = (
            request.form["school_name"]
        )

        school_settings["start_time"] = (
            request.form["start_time"]
        )

        school_settings["end_time"] = (
            request.form["end_time"]
        )

        school_settings["period_duration"] = int(
            request.form["period_duration"]
        )

        school_settings["number_of_periods"] = int(
            request.form["number_of_periods"]
        )

        school_settings["working_days"] = (
            request.form.getlist("working_days")
        )

        school_settings["break_start"] = (
            request.form["break_start"]
        )

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

        connection.execute("""
            INSERT INTO classes
            (class_name, section)

            VALUES (?, ?)
        """, (
            class_name,
            section
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("classes"))

    class_list = connection.execute("""
        SELECT *
        FROM classes
        ORDER BY class_name, section
    """).fetchall()

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

    connection.execute("""
        DELETE FROM classes
        WHERE id = ?
    """, (class_id,))

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

        connection.execute("""
            INSERT INTO teachers
            (teacher_name, subjects)

            VALUES (?, ?)
        """, (
            teacher_name,
            subjects
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("teachers"))

    teacher_list = connection.execute("""
        SELECT *
        FROM teachers
        ORDER BY teacher_name
    """).fetchall()

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

    connection.execute("""
        DELETE FROM teachers
        WHERE id = ?
    """, (teacher_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("teachers"))


# =========================================
# SUBJECTS
# =========================================

@app.route("/subjects", methods=["GET", "POST"])
def subjects():

    connection = get_db_connection()

    if request.method == "POST":

        subject_name = request.form["subject_name"].strip()

        periods_per_week = int(
            request.form["periods_per_week"]
        )

        connection.execute("""
            INSERT INTO subjects
            (subject_name, periods_per_week)

            VALUES (?, ?)
        """, (
            subject_name,
            periods_per_week
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("subjects"))

    subject_list = connection.execute("""
        SELECT *
        FROM subjects
        ORDER BY subject_name
    """).fetchall()

    connection.close()

    return render_template(
        "subjects.html",
        subjects=subject_list
    )


# =========================================
# DELETE SUBJECT
# =========================================

@app.route("/subjects/delete/<int:subject_id>")
def delete_subject(subject_id):

    connection = get_db_connection()

    connection.execute("""
        DELETE FROM subjects
        WHERE id = ?
    """, (subject_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("subjects"))


# =========================================
# ASSIGNMENTS
# =========================================

@app.route("/assignments", methods=["GET", "POST"])
def assignments():

    connection = get_db_connection()

    if request.method == "POST":

        class_id = int(
            request.form["class_id"]
        )

        subject_id = int(
            request.form["subject_id"]
        )

        teacher_id = int(
            request.form["teacher_id"]
        )

        periods_per_week = int(
            request.form["periods_per_week"]
        )

        connection.execute("""
            INSERT INTO assignments
            (
                class_id,
                subject_id,
                teacher_id,
                periods_per_week
            )

            VALUES (?, ?, ?, ?)
        """, (
            class_id,
            subject_id,
            teacher_id,
            periods_per_week
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("assignments"))

    class_list = connection.execute("""
        SELECT *
        FROM classes
        ORDER BY class_name, section
    """).fetchall()

    teacher_list = connection.execute("""
        SELECT *
        FROM teachers
        ORDER BY teacher_name
    """).fetchall()

    subject_list = connection.execute("""
        SELECT *
        FROM subjects
        ORDER BY subject_name
    """).fetchall()

    assignment_list = connection.execute("""
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

    """).fetchall()

    connection.close()

    return render_template(
        "assignments.html",
        classes=class_list,
        teachers=teacher_list,
        subjects=subject_list,
        assignments=assignment_list
    )


# =========================================
# DELETE ASSIGNMENT
# =========================================

@app.route("/assignments/delete/<int:assignment_id>")
def delete_assignment(assignment_id):

    connection = get_db_connection()

    connection.execute("""
        DELETE FROM assignments
        WHERE id = ?
    """, (assignment_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("assignments"))


# =========================================
# TIMETABLE GENERATOR
# =========================================

@app.route("/generate-timetable")
def generate_timetable():

    connection = get_db_connection()

    assignments = connection.execute("""
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

    """).fetchall()

    connection.close()

    # -----------------------------------------
    # Check assignments
    # -----------------------------------------

    if not assignments:

        return render_template(
            "timetable.html",
            timetable={},
            days=school_settings["working_days"],
            number_of_periods=school_settings["number_of_periods"],
            error="No assignments found. Please add teacher assignments first."
        )


    days = school_settings["working_days"]

    number_of_periods = school_settings["number_of_periods"]


    # -----------------------------------------
    # Create empty timetable
    # -----------------------------------------

    timetable = {}

    for class_id in set(
        assignment["class_id"]
        for assignment in assignments
    ):

        timetable[class_id] = {}

        for day in days:

            timetable[class_id][day] = {}

            for period in range(1, number_of_periods + 1):

                timetable[class_id][day][period] = None


    # -----------------------------------------
    # Teacher occupied slots
    # -----------------------------------------

    teacher_busy = set()


    # -----------------------------------------
    # Prepare lesson list
    # -----------------------------------------

    lessons = []

    for assignment in assignments:

        for _ in range(
            assignment["periods_per_week"]
        ):

            lessons.append({
                "class_id": assignment["class_id"],
                "subject_id": assignment["subject_id"],
                "teacher_id": assignment["teacher_id"],
                "class_name": assignment["class_name"],
                "section": assignment["section"],
                "subject_name": assignment["subject_name"],
                "teacher_name": assignment["teacher_name"]
            })


    # -----------------------------------------
    # Randomize lesson order
    # -----------------------------------------

    random.shuffle(lessons)


    # -----------------------------------------
    # Generate timetable
    # -----------------------------------------

    unscheduled_lessons = []


    for lesson in lessons:

        possible_slots = []

        for day in days:

            for period in range(
                1,
                number_of_periods + 1
            ):

                class_slot = (
                    lesson["class_id"],
                    day,
                    period
                )

                teacher_slot = (
                    lesson["teacher_id"],
                    day,
                    period
                )


                # Class already occupied
                if timetable[
                    lesson["class_id"]
                ][day][period] is not None:

                    continue


                # Teacher already occupied
                if teacher_slot in teacher_busy:

                    continue


                possible_slots.append(
                    (
                        day,
                        period
                    )
                )


        # -------------------------------------
        # Place lesson
        # -------------------------------------

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


    # -----------------------------------------
    # Display timetable
    # -----------------------------------------

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


# =========================================
# START APPLICATION
# =========================================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)