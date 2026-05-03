# 🎒 BAG — Budgeting Application for Students

BAG (Budgeting Application for Students) is a Flask-based web application designed to help students manage their finances throughout a semester. It allows users to track funding, expenses, and spending habits in a structured and visual way.

---

## 🚀 Features

* 📊 Dashboard with real-time financial insights
* 💰 Add and manage funding (financial aid, income, etc.)
* 💸 Track expenses by category
* 🧾 Statements page (full transaction history with income + expenses)
* 📅 Semester-based budgeting
* 📈 Spending analysis and projections
* 👨‍👩‍👧 Parent access view (optional)
* 🔐 Secure login with authentication

---

## 🖥️ Requirements

* Python 3.10 or higher
* pip (Python package manager)
* Virtual environment (recommended)

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd BAG-project-folder
```

---

### 2. Create and activate a virtual environment

#### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
```

#### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set environment variables

Create a `.env` file in the root folder and add:

```
SECRET_KEY=your_secret_key_here
```

---

### 5. Initialize the database

```bash
flask --app app init-db
```

---

### 6. Run the application

```bash
flask run
```

---

### 7. Open the application

Open your browser and go to:

```
http://127.0.0.1:5000/
```

---

## 👤 How to Use

1. Register a new account
2. Log in
3. Create your profile
4. Add a semester
5. Add funding (financial aid, income)
6. Add expenses
7. Use the navigation sidebar to access:

   * Dashboard (summary)
   * Statements (full financial history)
   * Budgeting (categories and limits)

---

## 🧾 Statements Page

The Statements page provides a complete financial history:

* Shows both income and expenses
* Displays transaction type (Income / Expense)
* Color-coded amounts:

  * Green = Income
  * Red = Expense
* Allows editing and deleting entries
* Combines funding and spending into one view (like a bank statement)

---

## 📁 Project Structure

```
app/
│
├── routes/
│   ├── dashboard.py
│   ├── transactions.py
│   ├── aid.py
│   ├── statements.py
│   └── ...
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── statements.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── images/
│   └── icons/
│
├── schema.sql
├── db.py
└── __init__.py
```

---

## 🛠️ Technologies Used

* Python (Flask)
* SQLite
* HTML / CSS (Jinja templates)
* JavaScript (Chart.js for visualizations)

---

## ⚠️ Notes

* This application runs on a development server (not for production use)
* The database must be initialized before running
* Restart Flask after making changes to code

---

## 👩‍💻 Author

Joey Ackerman-Lowery
Computer Programming Student

---

## 🤖 AI Usage

AI was used to assist with:

* Debugging and troubleshooting
* Code structure improvements
* Feature development (Statements page and enhancements)
* Documentation writing

All code was reviewed, tested, and integrated by the developer.
