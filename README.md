# 🎒 BAG — Budgeting Aid Guide

BAG (Budgeting Aid Guide) is a Flask-based financial management application developed to help students manage their finances throughout an academic semester. The application provides an organized and user-friendly platform for tracking funding, expenses, budgeting goals, and overall spending habits.

Originally developed as a collaborative Capstone project, BAG now supports both web-based development mode and a standalone Windows desktop executable.

---

# 🚀 Features

- Dashboard with real-time financial insights
- Add and manage funding sources (financial aid, income, etc.)
- Track expenses by category
- Statements page with complete transaction history
- Semester-based budgeting tools
- Spending analysis and financial projections
- Optional parent access view
- Secure login and registration system
- SQLite database integration
- Desktop executable (.exe) support
- Financial charts and visualizations

---

# 🖥️ Desktop Application Support

BAG can run as a standalone Windows desktop application without requiring Python or Visual Studio Code installation.

The desktop version was built using:

- Flask
- PyWebView
- PyInstaller
- SQLite3

---

# ▶️ Running the Desktop Application

## Run the Executable

1. Extract the project ZIP folder
2. Open the `dist` folder
3. Double-click:

```text
run.exe
```

---

# ⚠️ Important Notes

## Database Synchronization

The desktop application uses a synchronized SQLite database located in:

```text
dist/instance/bag.sqlite3
```

Do NOT remove or separate the `instance` folder from the executable.

---

## Windows Security Warning

If Windows Defender displays a warning:

1. Click **More Info**
2. Click **Run Anyway**

This warning is expected for locally built executables.

---

# 💻 Running in Development Mode

## Requirements

- Python 3.12+
- pip (Python package manager)

---

## Clone Repository

```bash
git clone https://github.com/CAPSTONE-Team-G0/BAG.git
```

---

## Open Project Folder

```bash
cd BAG
```

---

## Create Virtual Environment

```bash
py -m venv venv
```

---

## Activate Virtual Environment

### Windows PowerShell

```bash
.\venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install flask pywebview python-dotenv pyinstaller
```

---

## Initialize Database

```bash
flask --app app init-db
```

---

## Run Flask Development Server

```bash
flask run
```

Open browser:

```text
http://127.0.0.1:5000/
```

---

## Run Desktop Mode

```bash
python run.py
```

---

# 👤 How to Use

1. Register a new account
2. Log in
3. Create your user profile
4. Add a semester
5. Add funding sources (financial aid or income)
6. Add expenses
7. Use the sidebar to navigate through:

- Dashboard
- Statements
- Budgeting

---

# 🧾 Statements Page

The Statements page provides a complete financial history for the user.

Features include:

- Displays both income and expenses
- Shows transaction type (Income / Expense)
- Color-coded transaction amounts
  - Green = Income
  - Red = Expense
- Edit and delete transaction entries
- Combined funding and expense history view

---

# 📁 Project Structure

```text
app/
├── routes/
│   ├── dashboard.py
│   ├── transactions.py
│   ├── aid.py
│   ├── statements.py
│   └── ...
├── templates/
├── static/
├── schema.sql
├── db.py
└── __init__.py
```

---

# 🛠️ Technologies Used

- Python
- Flask
- SQLite3
- HTML / CSS
- JavaScript
- Chart.js
- PyWebView
- PyInstaller

---

# 📦 Packaging Information

The executable was built using:

```bash
pyinstaller --noconfirm --onefile --windowed ^
--add-data "app\templates;app\templates" ^
--add-data "app\static;app\static" ^
--add-data "app\schema.sql;app" ^
--icon "baglogotransparent2.ico" ^
run.py
```

---

# ⚠️ Additional Notes

- BAG runs on a development server while in development mode
- The database must be initialized before running Flask mode
- Restart Flask after making code changes
- The packaged executable automatically creates and manages the SQLite database beside the executable

---

# 👩‍💻 Team Members

- Joey Ackerman-Lowery
- Paul Gayle
- Mattea Isley
- Lydia Loffert

---

# © Intellectual Property & Copyright

BAG — Budgeting Aid Guide

Copyright © 2026 Group_0

Contributors:
- Joey Ackerman-Lowery
- Paul Gayle
- Mattea Isley
- Lydia Loffert

All rights reserved.

BAG (Budgeting Aid Guide), including its source code, application design,
database structure, executable builds, documentation, branding, and
associated materials, is proprietary intellectual property owned by Group_0.

Unauthorized copying, modification, distribution, sublicensing,
reverse engineering, or commercial use of this software or its
associated assets is strictly prohibited without prior written
permission from the copyright holders.

Logo and branding assets remain the intellectual property of
their respective creator unless otherwise agreed upon in writing.

---

# 🤖 AI Usage

Artificial intelligence tools were used to assist with debugging,
documentation, executable packaging, feature development, and workflow
support. All generated content was reviewed, tested, modified,
and implemented by the development team.
