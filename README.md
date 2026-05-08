

# 🎒 BAG — Budgeting Aid Guide

BAG (Budgeting Aid Guide) is a Flask-based financial management application designed to help students manage their finances throughout a semester. The application allows users to track funding, expenses, spending habits, and budgeting goals through an organized and user-friendly interface.

BAG was developed as a collaborative Capstone project and now supports both web-based development mode and a standalone Windows desktop executable.

---

# 🚀 Features

- Dashboard with real-time financial insights
- Add and manage funding (financial aid, income, etc.)
- Track expenses by category
- Statements page with full transaction history
- Semester-based budgeting
- Spending analysis and projections
- Parent access view (optional)
- Secure login and registration system
- SQLite database integration
- Desktop executable (.exe) support
- Financial charts and visualizations

---

# 🖥️ Desktop Application Support

BAG can now run as a standalone Windows desktop application without requiring VS Code or Python installation.

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

## Database Sync

The desktop application uses a synced SQLite database located in:

```text
dist/instance/bag.sqlite3
```

Do NOT remove or separate the `instance` folder from the executable.

---

## Windows Security Warning

If Windows Defender displays a warning:

1. Click **More Info**
2. Click **Run Anyway**

This is expected for locally built executables.

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

## Open Project Folder

```bash
cd BAG
```

## Create Virtual Environment

```bash
py -3.12 -m venv venv
```

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
3. Create your profile
4. Add a semester
5. Add funding (financial aid or income)
6. Add expenses
7. Use the sidebar to navigate:

- Dashboard
- Statements
- Budgeting

---

# 🧾 Statements Page

The Statements page provides a complete financial history:

- Displays both income and expenses
- Shows transaction type (Income / Expense)
- Color-coded amounts:
  - Green = Income
  - Red = Expense
- Allows editing and deleting entries
- Combines funding and expenses into one view

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

# ⚠️ Notes

- This project runs on a development server during development mode
- The database must be initialized before running in Flask mode
- Restart Flask after making code changes
- The packaged executable automatically creates and manages the SQLite database beside the executable

---

# 👩‍💻 Team Members

- Joey Ackerman-Lowery
- Paul Gayle
- Mattea Isley
- Lydia Loffert

---

# 🤖 AI Usage

AI was used to assist with debugging, executable packaging, feature development, and documentation. All work was reviewed, tested, and implemented by the team.
