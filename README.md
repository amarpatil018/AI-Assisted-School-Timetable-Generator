# AI-Assisted School Timetable Generator

A Flask-based school timetable management system that helps schools manage:

- Classes
- Sections
- Teachers
- Subjects
- Teacher assignments
- School timetable settings
- Automatic timetable generation
- Teacher conflict detection
- Class conflict detection
- Unscheduled lesson detection

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- Jinja2

## Project Structure

AI-Assisted School Timetable Generator/

├── app.py

├── README.md

├── school.db

├── templates/

│   ├── index.html

│   ├── settings.html

│   ├── classes.html

│   ├── teachers.html

│   ├── subjects.html

│   ├── assignments.html

│   └── timetable.html

└── static/

    └── style.css

## How to Run

Open the project folder in Visual Studio Code.

Open the terminal.

Install Flask:

pip install flask

Run the application:

python app.py

Open the following URL:

http://127.0.0.1:5000

## Main Workflow

1. Configure school settings.
2. Add classes and sections.
3. Add teachers.
4. Add subjects.
5. Create teacher assignments.
6. Generate the timetable.
7. Review conflicts and unscheduled lessons.

## Timetable Generation

The generator checks:

- Class availability
- Teacher availability
- Weekly lesson requirements
- Timetable capacity
- Teacher scheduling conflicts
- Unscheduled lessons

## Database

SQLite is used as the database.

The database file `school.db` is automatically created when the application starts.