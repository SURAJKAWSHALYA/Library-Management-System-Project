# 📚 Library Management System

A modern web-based **Library Management System** developed using **Python Flask, HTML, CSS, JavaScript, and SQLite**.
This system helps librarians and students efficiently manage books, borrowing activities, return tracking, and student records through an interactive and responsive web interface.

---

# 🎯 Overview

This project is designed to digitize traditional library operations and provide an easy-to-use management platform for schools, universities, and organizations.

The system includes:

* 👨‍🎓 Student Management
* 📚 Book Management
* 🔄 Borrow & Return System
* 👨‍💼 Librarian Dashboard
* 📊 Library Statistics
* 🔍 Smart Search Features
* 🔐 Authentication & Security

---

# ✨ Features

## 📚 Book Management

* Add New Books
* Edit Book Details
* Delete Books
* Book Availability Tracking
* Category Management

---

## 👨‍🎓 Student Features

* Student Registration
* Login System
* Borrow Books
* Return Books
* Borrow History
* Due Date Tracking

---

## 👨‍💼 Librarian Features

* Approve Borrow Requests
* Manage Student Records
* Calculate Fines
* View Borrow Statistics
* Manage Returned Books

---

# 🏗️ Technology Stack

## 🌐 Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap (Optional)

---

## ⚙️ Backend

* Python 3
* Flask Framework

---

## 🗄️ Database

* SQLite3 (`library.db`)

---

# 📁 Project Structure

```bash
Library_Management_System/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   ├── style.css
│   └── script.js
│
├── templates/
│   ├── admin/
│   ├── librarian/
│   ├── student/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── books.html
│
├── app.py
├── init_db.py
├── library.db
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🚀 Installation

## 📌 Prerequisites

* Python 3.10+
* VS Code
* Git

---

# ⚡ Setup Instructions

## Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
```

---

## Step 2: Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install flask
```

Or:

```bash
pip install -r requirements.txt
```

---

## Step 4: Run Application

```bash
python app.py
```

---

# 🌐 Access the Application

```bash
http://127.0.0.1:5000
```

---

# 📚 System Modules

## 👨‍🎓 Student Panel

* Search Books
* Send Borrow Requests
* Return Borrowed Books
* View Borrow History

---

## 👨‍💼 Librarian Panel

* Approve Requests
* Add/Edit/Delete Books
* Manage Students
* View Library Reports

---

# 📊 Database Tables

## 📖 Books Table

```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    category TEXT,
    quantity INTEGER
);
```

---

## 👨‍🎓 Students Table

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
);
```

---

## 🔄 Borrow Records Table

```sql
CREATE TABLE borrow_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    book_id INTEGER,
    issue_date TEXT,
    return_date TEXT,
    status TEXT
);
```

---

# 🔐 Security Features

* Session-Based Authentication
* Password Hashing
* Protected Routes
* Input Validation
* SQL Injection Prevention

---

# 📈 Dashboard Features

* Total Books Counter
* Total Students Counter
* Borrowed Books Statistics
* Returned Books Statistics
* Fine Calculation System

---

# 📱 Responsive Design

* Mobile Friendly
* Tablet Compatible
* Desktop Optimized

---

# ⚙️ Advanced Features

✅ Borrow Approval System
✅ Return Management
✅ Fine Calculation
✅ Dynamic Dashboard
✅ Real-Time Book Availability
✅ Student Record Management

---

# 🐛 Troubleshooting

## Flask Not Installed

```bash
pip install flask
```

---

## Database Error

```bash
Delete library.db and run init_db.py again
```

---

## Port Already Running

```python
app.run(debug=True, port=5001)
```

---

# ☁️ Future Enhancements

* QR Code Scanner
* Barcode Support
* Email Notifications
* AI Book Recommendation
* Dark Mode
* Online Cloud Database
* Mobile Application

---

# 🎓 Learning Outcomes

This project helps understand:

* Flask Web Development
* CRUD Operations
* Database Management
* Authentication Systems
* Frontend & Backend Integration
* Session Handling
* Responsive Web Design

---

# 📄 License

This project is for educational purposes only.

---

# 🙏 Acknowledgments

* Python Community
* Flask Framework
* SQLite
* Open Source Contributors

---

# 📞 Support

For issues and questions:

* Check Flask Errors
* Verify Database Connection
* Ensure Dependencies Are Installed
* Review Console Logs

---

# 🎯 Key Takeaways

✅ Complete Library Management System
✅ Built Using Flask + SQLite
✅ Responsive User Interface
✅ Student & Librarian Management
✅ Borrow & Return Tracking
✅ Beginner-Friendly Full Stack Project

---

# ❤️ Developed By

**Suraj**
Software Engineering Student
Passionate about Full Stack Development & Smart Systems
