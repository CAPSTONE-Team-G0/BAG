# 🎒 BAG — Budgeting Aid Guide

BAG (Budgeting Aid Guide) is a Flask-based web application designed to help students manage their finances throughout a semester. It allows users to track funding, expenses, and spending habits in a structured and visual way.

---

## 🚀 Features

* Dashboard with real-time financial insights
* Add and manage funding (financial aid, income, etc.)
* Track expenses by category
* Statements page (full transaction history with income + expenses)
* Semester-based budgeting
* Spending analysis and projections
* Parent access view (optional)
* Secure login system

---

## 🖥️ Requirements

* Python 3.10 or higher
* pip (Python package manager)

---

## ▶️ Terminal Steps to Run the Project

Open PowerShell or the VS Code terminal.

Clone the repository:
```
git clone https://github.com/CAPSTONE-Team-G0/BAG.git
```
Go into the project folder:
```
cd BAG
```
Create a virtual environment:
```
python -m venv venv
```
Activate the virtual environment:
```
venv\Scripts\activate
```
(You should now see (venv) at the start of your terminal line)

Install required packages:
```
pip install -r requirements.txt
```
Initialize the database:
```
flask --app app init-db
```
Run the Flask application:
```
flask run
```
Open your browser and go to:

http://127.0.0.1:5000/

To stop the server:

CTRL + C

---

## 👤 How to Use

1. Register a new account
2. Log in
3. Create your profile
4. Add a semester
5. Add funding (financial aid or income)
6. Add expenses
7. Use the sidebar to navigate:

   * Dashboard
   * Statements
   * Budgeting

---

## 🧾 Statements Page

The Statements page provides a complete financial history:

* Shows both income and expenses
* Displays transaction type (Income / Expense)
* Color-coded amounts:

  * Green = Income
  * Red = Expense
* Allows editing and deleting entries
* Combines funding and expenses into one view

---

## 📁 Project Structure

```
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

## 🛠️ Technologies Used

* Python (Flask)
* SQLite
* HTML / CSS
* JavaScript (Chart.js)

---

## ⚠️ Notes

* This project runs on a development server
* The database must be initialized before running
* Restart Flask after making changes

---

## 👩‍💻 Team Members

* Joey Ackerman-Lowery
* Paul Gayle
* Mattea Isley
* Lydia Loffert

---

## 🤖 AI Usage

AI was used to assist with debugging, feature development, and documentation. All work was reviewed, tested, and implemented by the Team.

