# BAG — Semester-Based Financial Pacing App

BAG is a Flask + SQLite web app that helps students manage financial aid, track expenses, and monitor spending across a semester. It allows users to create an account, set up a profile, create semesters, add aid and transactions, and view a dashboard that compares spending pace against semester progress.

## Features

* User registration, login, and logout
* Profile setup
* Semester creation and selection
* Financial aid entry
* Income and expense tracking
* Category tracking
* Dashboard with:

  * current week of semester
  * percent of semester elapsed
  * percent of funds spent
  * safe-to-spend amount
  * pacing alerts
  * category totals
  * run-out projection

## Tech Stack

* Python
* Flask
* Jinja2
* SQLite
* HTML/CSS

## Project Structure

```
BAG/
│
├── app/
├── instance/
├── tests/
├── requirements.txt
├── wsgi.py
├── README.md
└── README_MODULARIZED.md
```

## Requirements

Before running the program, install:

* Python 3.10 or newer
* pip
* VS Code or another code editor

## Setup Instructions

### 1. Clone or download the repository

```
git clone https://github.com/CAPSTONE-Team-G0/BAG.git
cd BAG
```

### 2. Create a virtual environment

#### Windows PowerShell

```
python -m venv venv
venv\Scripts\Activate.ps1
```

If PowerShell asks whether to trust the script, choose:

```
R = Run once
```

#### Windows Command Prompt

```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

## Initialize the Database

Before running the app for the first time, initialize the database.

### Windows PowerShell

```
$env:FLASK_APP="app"
flask init-db
```

### Windows Command Prompt

```
set FLASK_APP=app
flask init-db
```

## Run the Application

### PowerShell

```
flask --app app --debug run
```

### Command Prompt

```
flask --app app --debug run
```

Then open this in your browser:

```
http://127.0.0.1:5000
```

## How to Use the App

1. Register a new account
2. Log in
3. Create your profile
4. Create a semester
5. Select the semester
6. Add financial aid
7. Add income and expense transactions
8. Open the dashboard to review your financial pace

## Running Tests

```
pytest -q
```

## Troubleshooting

### Python not found

Make sure Python is installed and added to PATH.

### Virtual environment will not activate

Use Command Prompt instead of PowerShell, or allow the script to run once in PowerShell.

### Flask app will not start

Make sure you installed dependencies:

```
pip install -r requirements.txt
```

### Database errors

Run:

```
flask init-db
```

before starting the app.

### Internal Server Error after login

Check the VS Code terminal for the exact error message and update any outdated route names (for example, replace `core.dashboard` with `dashboard.dashboard`).

## Notes

* Currency values are stored in cents
* The active semester is stored in session data
* SQLite is used for local storage

## Contributors

CAPSTONE-Team-G0
