from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
import os


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = "smart-school-timetable-secret-key"


# ============================================================
# DATABASE
# ============================================================

DATABASE = "school.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    # Enable foreign keys
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# SCHOOL SETTINGS
# ============================================================

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


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():

    connection = get_db_connection()

    # --------------------------------------------------------
    # Classes
    # --------------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            section TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # Teachers
    # --------------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            subjects TEXT
        )
    """)

    # --------------------------------------------------------
    # Subjects
    # --------------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            periods_per_week INTEGER NOT NULL DEFAULT 1
        )
    """)

    # --------------------------------------------------------
    # Assignments
    # --------------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            periods_per_week INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (class_id)
                REFERENCES classes(id)
                ON DELETE CASCADE,

            FOREIGN KEY (subject_id)
                REFERENCES subjects(id)
                ON DELETE CASCADE,

            FOREIGN KEY (teacher_id)
                REFERENCES teachers(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()

    # --------------------------------------------------------
    # Make sure old databases have the subjects column
    # --------------------------------------------------------

    teacher_columns = connection.execute(
        "PRAGMA table_info(teachers)"
    ).fetchall()

    teacher_column_names = [
        column["name"] for column in teacher_columns
    ]

    if "subjects" not in teacher_column_names:

        connection.execute("""
            ALTER TABLE teachers
            ADD COLUMN subjects TEXT
        """)

        connection.commit()

    connection.close()


# Initialize database when application starts
initialize_database()


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/")
def home():

    connection = get_db_connection()

    class_count = connection.execute(
        "SELECT COUNT(*) AS count FROM classes"
    ).fetchone()["count"]

    teacher_count = connection.execute(
        "SELECT COUNT(*) AS count FROM teachers"
    ).fetchone()["count"]

    subject_count = connection.execute(
        "SELECT COUNT(*) AS count FROM subjects"
    ).fetchone()["count"]

    assignment_count = connection.execute(
        "SELECT COUNT(*) AS count FROM assignments"
    ).fetchone()["count"]

    connection.close()

    return render_template(
        "index.html",
        class_count=class_count,
        teacher_count=teacher_count,
        subject_count=subject_count,
        assignment_count=assignment_count
    )


# ============================================================
# SETTINGS
# ============================================================

@app.route("/settings", methods=["GET", "POST"])
def settings():

    global school_settings

    if request.method == "POST":

        school_name = request.form.get(
            "school_name",
            ""
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
            "7"
        )

        break_start = request.form.get(
            "break_start",
            "12:00"
        )

        break_duration = request.form.get(
            "break_duration",
            "30"
        )

        # ----------------------------------------------------
        # Working days
        # ----------------------------------------------------

        working_days = request.form.getlist(
            "working_days"
        )

        # If no days are selected, use Monday-Friday
        if not working_days:

            working_days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday"
            ]

        # ----------------------------------------------------
        # Convert numeric values safely
        # ----------------------------------------------------

        try:
            period_duration = int(period_duration)
        except ValueError:
            period_duration = 45

        try:
            number_of_periods = int(number_of_periods)
        except ValueError:
            number_of_periods = 7

        try:
            break_duration = int(break_duration)
        except ValueError:
            break_duration = 30

        # ----------------------------------------------------
        # Save settings
        # ----------------------------------------------------

        school_settings = {
            "school_name": school_name
            if school_name
            else "AI-Assisted School Timetable Generator",

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
        settings=school_settings,
        school_settings=school_settings
    )


# ============================================================
# CLASSES
# ============================================================

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
                (
                    class_name,
                    section
                )
            )

            connection.commit()

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
        classes=class_list,
        class_list=class_list
    )


# ============================================================
# DELETE CLASS
# ============================================================

@app.route("/classes/delete/<int:id>")
def delete_class(id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM classes
        WHERE id = ?
        """,
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("classes"))


# ============================================================
# TEACHERS
# ============================================================

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
                (
                    teacher_name,
                    subjects
                )
            )

            connection.commit()

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
        teachers=teacher_list,
        teacher_list=teacher_list
    )


# ============================================================
# DELETE TEACHER
# ============================================================

@app.route("/teachers/delete/<int:id>")
def delete_teacher(id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM teachers
        WHERE id = ?
        """,
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("teachers"))


# ============================================================
# SUBJECTS
# ============================================================

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
            "1"
        )

        try:
            periods_per_week = int(
                periods_per_week
            )
        except ValueError:
            periods_per_week = 1

        if periods_per_week < 1:
            periods_per_week = 1

        if subject_name:

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
        subjects=subject_list,
        subject_list=subject_list
    )


# ============================================================
# DELETE SUBJECT
# ============================================================

@app.route("/subjects/delete/<int:id>")
def delete_subject(id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM subjects
        WHERE id = ?
        """,
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("subjects"))


# ============================================================
# ASSIGNMENTS
# ============================================================

@app.route("/assignments", methods=["GET", "POST"])
def assignments():

    connection = get_db_connection()

    # --------------------------------------------------------
    # Add assignment
    # --------------------------------------------------------

    if request.method == "POST":

        class_id = request.form.get(
            "class_id"
        )

        subject_id = request.form.get(
            "subject_id"
        )

        teacher_id = request.form.get(
            "teacher_id"
        )

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

            return redirect(
                url_for("assignments")
            )

        if periods_per_week < 1:
            periods_per_week = 1

        # ----------------------------------------------------
        # Prevent duplicate assignment
        # ----------------------------------------------------

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

            # Update existing assignment
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

    # --------------------------------------------------------
    # Get classes
    # --------------------------------------------------------

    class_list = connection.execute(
        """
        SELECT *
        FROM classes
        ORDER BY class_name, section
        """
    ).fetchall()

    # --------------------------------------------------------
    # Get teachers
    # --------------------------------------------------------

    teacher_list = connection.execute(
        """
        SELECT *
        FROM teachers
        ORDER BY teacher_name
        """
    ).fetchall()

    # --------------------------------------------------------
    # Get subjects
    # --------------------------------------------------------

    subject_list = connection.execute(
        """
        SELECT *
        FROM subjects
        ORDER BY subject_name
        """
    ).fetchall()

    # --------------------------------------------------------
    # Get assignments with names
    # --------------------------------------------------------

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

            subjects.periods_per_week AS subject_periods,

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
        class_list=class_list,

        teachers=teacher_list,
        teacher_list=teacher_list,

        subjects=subject_list,
        subject_list=subject_list,

        assignments=assignment_list,
        assignment_list=assignment_list
    )


# ============================================================
# DELETE ASSIGNMENT
# ============================================================

@app.route("/assignments/delete/<int:id>")
def delete_assignment(id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM assignments
        WHERE id = ?
        """,
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("assignments")
    )


# ============================================================
# TIMETABLE GENERATOR
# ============================================================

@app.route("/generate-timetable")
def generate_timetable():

    connection = get_db_connection()

    assignments = connection.execute(
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

            subjects.periods_per_week AS subject_periods,

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
            subjects.subject_name
        """
    ).fetchall()

    connection.close()

    # --------------------------------------------------------
    # No assignments
    # --------------------------------------------------------

    if not assignments:

        return render_template(
            "timetable.html",

            timetable={},

            days=school_settings["working_days"],

            number_of_periods=school_settings[
                "number_of_periods"
            ],

            class_information={},

            unscheduled=[],

            error=(
                "No assignments found. "
                "Please add classes, teachers, "
                "subjects and assignments first."
            )
        )

    days = school_settings["working_days"]

    number_of_periods = school_settings[
        "number_of_periods"
    ]

    # --------------------------------------------------------
    # Validate working days
    # --------------------------------------------------------

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
                "Please open Settings and select "
                "at least one working day."
            )
        )

    # --------------------------------------------------------
    # Total available slots
    # --------------------------------------------------------

    total_slots_per_class = (
        len(days) * number_of_periods
    )

    # --------------------------------------------------------
    # Create timetable structure
    # --------------------------------------------------------

    timetable = {}

    class_information = {}

    for assignment in assignments:

        class_id = assignment["class_id"]

        class_information[class_id] = {

            "class_name":
                assignment["class_name"],

            "section":
                assignment["section"]
        }

        if class_id not in timetable:

            timetable[class_id] = {}

            for day in days:

                timetable[class_id][day] = {}

                for period in range(
                    1,
                    number_of_periods + 1
                ):

                    timetable[class_id][day][
                        period
                    ] = None

    # --------------------------------------------------------
    # Create individual lessons
    # --------------------------------------------------------

    lessons = []

    for assignment in assignments:

        periods = assignment[
            "periods_per_week"
        ]

        for lesson_number in range(periods):

            lessons.append({

                "assignment_id":
                    assignment["id"],

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
                    assignment["teacher_name"],

                "lesson_number":
                    lesson_number + 1
            })

    # --------------------------------------------------------
    # Capacity check
    # --------------------------------------------------------

    capacity_errors = []

    class_requested_periods = {}

    for lesson in lessons:

        class_id = lesson["class_id"]

        if class_id not in class_requested_periods:

            class_requested_periods[class_id] = 0

        class_requested_periods[class_id] += 1

    for class_id, requested in class_requested_periods.items():

        if requested > total_slots_per_class:

            class_name = class_information[
                class_id
            ]["class_name"]

            section = class_information[
                class_id
            ]["section"]

            capacity_errors.append(
                f"{class_name} - Section {section} "
                f"requires {requested} periods but only "
                f"{total_slots_per_class} periods are available."
            )

    # --------------------------------------------------------
    # Shuffle lessons
    # --------------------------------------------------------

    random.shuffle(lessons)

    # --------------------------------------------------------
    # Teacher busy slots
    # --------------------------------------------------------

    teacher_busy = set()

    # --------------------------------------------------------
    # Track subject daily usage
    # --------------------------------------------------------

    subject_daily_count = {}

    # --------------------------------------------------------
    # Track unscheduled lessons
    # --------------------------------------------------------

    unscheduled_lessons = []

    # --------------------------------------------------------
    # Generate timetable
    # --------------------------------------------------------

    for lesson in lessons:

        possible_slots = []

        for day in days:

            for period in range(
                1,
                number_of_periods + 1
            ):

                # --------------------------------------------
                # Class already occupied?
                # --------------------------------------------

                if timetable[
                    lesson["class_id"]
                ][day][period] is not None:

                    continue

                # --------------------------------------------
                # Teacher already teaching?
                # --------------------------------------------

                teacher_slot = (
                    lesson["teacher_id"],
                    day,
                    period
                )

                if teacher_slot in teacher_busy:

                    continue

                # --------------------------------------------
                # Subject daily limit
                # Maximum 2 lessons of same subject/day
                # --------------------------------------------

                subject_day_key = (
                    lesson["class_id"],
                    lesson["subject_id"],
                    day
                )

                current_subject_count = (
                    subject_daily_count.get(
                        subject_day_key,
                        0
                    )
                )

                if current_subject_count >= 2:

                    continue

                possible_slots.append(
                    (day, period)
                )

        # ----------------------------------------------------
        # Put lesson into timetable
        # ----------------------------------------------------

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

            subject_day_key = (
                lesson["class_id"],
                lesson["subject_id"],
                day
            )

            subject_daily_count[
                subject_day_key
            ] = subject_daily_count.get(
                subject_day_key,
                0
            ) + 1

        else:

            unscheduled_lessons.append(
                lesson
            )

    # --------------------------------------------------------
    # Final error message
    # --------------------------------------------------------

    error = None

    if capacity_errors:

        error = " ".join(capacity_errors)

    # --------------------------------------------------------
    # Render timetable
    # --------------------------------------------------------

    return render_template(

        "timetable.html",

        timetable=timetable,

        days=days,

        number_of_periods=number_of_periods,

        class_information=class_information,

        unscheduled=unscheduled_lessons,

        error=error,

        school_settings=school_settings
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )