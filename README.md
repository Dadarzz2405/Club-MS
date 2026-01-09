# Rohis Management System

The **Rohis Management System** is a web-based application developed to support the digital management of **Rohis (Rohani Islam)** activities in schools.
This system helps administrators manage member data and attendance records efficiently, replacing manual and paper-based processes.

## 🎯 Project Objectives

* Digitize Rohis member and attendance management
* Improve accuracy and accessibility of attendance data
* Practice real-world web development using Python and Flask
* Apply database design and authentication concepts in a practical project

## ✨ Key Features

* 🔐 Secure login system (Admin & Member)
* 👥 Rohis member management
* 📅 Attendance recording for Rohis activities
* 📊 Attendance history view (admin access)
* 🧑‍💼 Admin dashboard for monitoring data
* 📂 Simple and structured user interface

## 🛠️ Technologies Used

* **Backend:** Python (Flask)
* **Frontend:** HTML, CSS, Jinja2
* **Database:** SQLite
* **Authentication:** Flask-Login
* **ORM:** SQLAlchemy

## 📁 Project Structure

```
├── app.py
├── models.py
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── attendance_history_admin.html
│   └── ...
├── static/
│   └── style.css
├── instance/
│   └── database.db
└── README.md
```

## 🚀 Installation Guide

1. Clone this repository

```bash
git clone https://github.com/yourusername/rohis-management-system.git
cd rohis-management-system
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

3. Install required dependencies

```bash
pip install -r requirements.txt
```

4. Run the application

```bash
python app.py
```

5. Open the application in your browser

```
http://127.0.0.1:5000
```

## 🧠 Learning Outcomes

Through this project, the developer gained experience in:

* Flask routing and template rendering
* User authentication and access control
* Relational database management using SQLAlchemy
* Building CRUD-based web applications
* Structuring and documenting a software project

## 📈 Future Development Plans

* Attendance data export (Excel / PDF)
* Attendance analytics and statistics
* Role-based permission system
* Mobile-responsive user interface

## 👤 Developer

**Dadarzz**
---
Haidar Ali Fawwaz Nasirodin

This project was developed as a **school project and personal portfolio**, demonstrating practical application of web development concepts.

## ⚠️ Notes & Limitations

Please note that this project is **small in scale** and is **not yet capable of supporting larger or more complex activities**.
It was developed primarily for learning purposes and basic Rohis management needs, and may require further development and optimization for broader or long-term use.
