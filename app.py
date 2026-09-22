from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary school settings
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


# -----------------------------------------
# HOME / DASHBOARD
# -----------------------------------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        settings=school_settings
    )


# -----------------------------------------
# SCHOOL SETTINGS
# -----------------------------------------

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


# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------

if __name__ == "__main__":
    app.run(debug=True)