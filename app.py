from flask import Flask, render_template, request, redirect, url_for
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
# SCHOOL SETTINGS
# =========================================

school_settings = {
    "school_name": "SmartSchool",
    "start_time": "09:00",
    "end_time": "16:00",
    "period_duration": 45,
    "number_of_periods": 7,
    "working_days": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ],
    "break_start": "12:15",
    "break_duration": 30
}


# =========================================
# DATABASE INITIALIZATION
# =========================================

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


initialize_database()


# =========================================
# DASHBOARD
# =========================================

@app.route("/")
def index():

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


# =========================================
# SETTINGS
# =========================================

@app.route("/settings", methods=["GET", "POST"])
def settings():

    if request.method == "POST":

        school_settings["school_name"] = request.form.get(
            "school_name",
            "SmartSchool"
        )

        school_settings["start_time"] = request.form.get(
            "start_time",
            "09:00"
        )

        school_settings["end_time"] = request.form.get(
            "end_time",
            "16:00"
        )

        school_settings["period_duration"] = int(
            request.form.get(
                "period_duration",
                45
            )
        )

        school_settings["number_of_periods"] = int(
            request.form.get(
                "number_of_periods",
                7
            )
        )

        school_settings["break_start"] = request.form.get(
            "break_start",
            "12:15"
        )

        school_settings["break_duration"] = int(
            request.form.get(
                "break_duration",
                30
            )
        )

        school_settings["working_days"] = request.form.getlist(
            "working_days"
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
        classes=class_list
    )


@app.route("/classes/delete/<int:id>")
def delete_class(id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM classes WHERE id = ?",
        (id,)
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
        teachers=teacher_list
    )


@app.route("/teachers/delete/<int:id>")
def delete_teacher(id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM teachers WHERE id = ?",
        (id,)
    )

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

        subject_name = request.form.get(
            "subject_name",
            ""
        ).strip()

        periods_per_week = int(
            request.form.get(
                "periods_per_week",
                1
            )
        )

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


@app.route("/subjects/delete/<int:id>")
def delete_subject(id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM subjects WHERE id = ?",
        (id,)
    )

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

        # Check whether this exact
        # assignment already exists.

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


@app.route("/assignments/delete/<int:id>")
def delete_assignment(id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM assignments WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("assignments"))


# =========================================
# AUTOMATIC TIMETABLE GENERATOR
# =========================================

@app.route("/generate-timetable")
def generate_timetable():

    connection = get_db_connection()

    assignments = connection.execute("""
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
            classes.section
    """).fetchall()

    connection.close()


    # =====================================
    # SETTINGS
    # =====================================

    days = school_settings["working_days"]

    number_of_periods = school_settings[
        "number_of_periods"
    ]


    validation_errors = []

    conflicts = []

    unscheduled_lessons = []


    # =====================================
    # BASIC VALIDATION
    # =====================================

    if not days:

        validation_errors.append(
            "No working days are configured. "
            "Please select at least one working day "
            "in Settings."
        )


    if number_of_periods <= 0:

        validation_errors.append(
            "The number of periods must be greater "
            "than zero."
        )


    if not assignments:

        validation_errors.append(
            "No teacher assignments were found. "
            "Please create teacher assignments first."
        )


    if validation_errors:

        return render_template(
            "timetable.html",

            timetable={},

            days=days,

            number_of_periods=number_of_periods,

            class_information={},

            unscheduled=[],

            conflicts=[],

            validation_errors=validation_errors,

            break_start=school_settings[
                "break_start"
            ],

            break_duration=school_settings[
                "break_duration"
            ]
        )


    # =====================================
    # CAPACITY CHECK
    # =====================================

    available_periods = (
        len(days) * number_of_periods
    )

    class_totals = {}


    for assignment in assignments:

        class_id = assignment["class_id"]

        class_totals[class_id] = (
            class_totals.get(
                class_id,
                0
            )
            +
            assignment["periods_per_week"]
        )


    capacity_errors = []


    for assignment in assignments:

        class_id = assignment["class_id"]

        if (
            class_totals[class_id]
            >
            available_periods
        ):

            capacity_errors.append(

                f"{assignment['class_name']} "
                f"{assignment['section']} requires "
                f"{class_totals[class_id]} periods, "
                f"but only "
                f"{available_periods} periods are "
                f"available per week."

            )


    capacity_errors = list(
        dict.fromkeys(capacity_errors)
    )


    # =====================================
    # CREATE EMPTY TIMETABLE
    # =====================================

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

                    timetable[
                        class_id
                    ][day][period] = None


    # =====================================
    # CREATE LESSON LIST
    # =====================================

    lessons = []


    assignment_validation_errors = []


    for assignment in assignments:

        assignment_periods = (
            assignment["periods_per_week"]
        )

        subject_periods = (
            assignment["subject_periods"]
        )


        if assignment_periods <= 0:

            assignment_validation_errors.append(

                f"{assignment['subject_name']} "
                f"for "
                f"{assignment['class_name']} "
                f"{assignment['section']} "
                f"has an invalid weekly "
                f"period value."

            )

            continue


        # Detect mismatch between
        # subject configuration and assignment.

        if assignment_periods != subject_periods:

            assignment_validation_errors.append(

                f"{assignment['subject_name']} "
                f"for "
                f"{assignment['class_name']} "
                f"{assignment['section']} "
                f"is assigned "
                f"{assignment_periods} "
                f"periods/week, while the "
                f"subject is configured for "
                f"{subject_periods} "
                f"periods/week."

            )


        # Expand weekly periods into
        # individual lessons.

        for lesson_number in range(
            assignment_periods
        ):

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


    # =====================================
    # RANDOMIZE LESSONS
    # =====================================

    random.shuffle(lessons)


    # =====================================
    # TRACK TEACHER OCCUPANCY
    # =====================================

    teacher_busy = set()


    # =====================================
    # PLACE LESSONS
    # =====================================

    for lesson in lessons:

        possible_slots = []


        for day in days:

            for period in range(
                1,
                number_of_periods + 1
            ):

                # ---------------------------------
                # CLASS CONFLICT CHECK
                # ---------------------------------

                if (
                    timetable[
                        lesson["class_id"]
                    ][day][period]
                    is not None
                ):

                    continue


                # ---------------------------------
                # TEACHER CONFLICT CHECK
                # ---------------------------------

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


        # =================================
        # PLACE LESSON
        # =================================

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


    # =====================================
    # VERIFY TEACHER CONFLICTS
    # =====================================

    teacher_schedule = {}


    for class_id in timetable:

        for day in timetable[class_id]:

            for period in timetable[
                class_id
            ][day]:

                lesson = timetable[
                    class_id
                ][day][period]


                if lesson is None:
                    continue


                teacher_id = lesson[
                    "teacher_id"
                ]


                key = (

                    teacher_id,
                    day,
                    period

                )


                if key not in teacher_schedule:

                    teacher_schedule[key] = []


                teacher_schedule[
                    key
                ].append(lesson)


    for key, lesson_list in (
        teacher_schedule.items()
    ):

        if len(lesson_list) > 1:

            teacher_name = lesson_list[
                0
            ]["teacher_name"]


            conflicts.append(

                f"Teacher conflict: "
                f"{teacher_name} is assigned "
                f"to more than one class on "
                f"{key[1]}, Period {key[2]}."

            )


    conflicts = list(
        dict.fromkeys(conflicts)
    )


    # =====================================
    # FINAL VALIDATION
    # =====================================

    validation_errors.extend(
        capacity_errors
    )

    validation_errors.extend(
        assignment_validation_errors
    )

    validation_errors = list(
        dict.fromkeys(validation_errors)
    )


    # =====================================
    # DISPLAY TIMETABLE
    # =====================================

    return render_template(

        "timetable.html",

        timetable=timetable,

        days=days,

        number_of_periods=
            number_of_periods,

        class_information=
            class_information,

        unscheduled=
            unscheduled_lessons,

        conflicts=
            conflicts,

        validation_errors=
            validation_errors,

        break_start=
            school_settings[
                "break_start"
            ],

        break_duration=
            school_settings[
                "break_duration"
            ]

    )


# =========================================
# START FLASK APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )