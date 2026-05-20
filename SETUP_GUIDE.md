# 🚀 Quick Setup Guide

## Installation & Setup (5 minutes)

### Step 1: Open Terminal in Project Directory
```bash
cd "D:\PROJECTS\Library Management System"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Initialize Database
```bash
python init_db.py
```

This will:
- ✅ Create SQLite database
- ✅ Create all tables
- ✅ Add admin user (username: admin, password: admin123)
- ✅ Add sample books

### Step 6: Run Application
```bash
python app.py
```

### Step 7: Access in Browser
```
http://127.0.0.1:5000
```

---

## 📋 Features Checklist

### ✅ Authentication
- [x] User Registration
- [x] User Login
- [x] Password Hashing
- [x] Session Management
- [x] Logout
- [x] Flash Messages

### ✅ Dashboard
- [x] Statistics Cards
- [x] Recent Books
- [x] Quick Actions
- [x] User Activity

### ✅ Book Management
- [x] Add Books
- [x] View Books (Paginated)
- [x] Search & Filter
- [x] Edit Books
- [x] Delete Books

### ✅ Borrowing System
- [x] Borrow Books
- [x] Return Books
- [x] Fine Calculation
- [x] Borrow History
- [x] Due Date Tracking

### ✅ User Management
- [x] User Profiles
- [x] Settings
- [x] Password Change
- [x] Admin User Management

### ✅ UI/UX
- [x] Responsive Design
- [x] Dark Theme
- [x] Glassmorphism
- [x] Smooth Animations
- [x] Mobile Friendly
- [x] Professional Layout

---

## 🔑 Default Login Credentials

**Username:** `admin`
**Password:** `admin123`

⚠️ **Change password after first login!**

---

## 📁 Project Structure

```
Library Management System/
├── app.py                          # Main Flask application
├── init_db.py                      # Database initialization script
├── requirements.txt                # Python dependencies
├── README.md                       # Full documentation
├── SETUP_GUIDE.md                  # This file
│
├── templates/                      # HTML Templates
│   ├── base.html                   # Base template
│   ├── login.html & register.html  # Auth pages
│   ├── dashboard.html              # Main dashboard
│   ├── books.html                  # Books listing
│   ├── add_book.html & edit_book.html
│   ├── borrow.html & return.html   # Borrowing
│   ├── history.html                # History page
│   ├── settings.html               # Settings page
│   ├── admin_users.html            # Admin panel
│   └── 404.html & 500.html         # Error pages
│
├── static/
│   ├── css/
│   │   ├── style.css               # Main stylesheet
│   │   └── auth.css                # Auth pages styling
│   └── js/
│       └── script.js               # JavaScript functionality
│
└── database.db                     # SQLite database (auto-created)
```

---

## 🛠️ Common Issues & Solutions

### Port 5000 Already in Use
**Solution:** Change port in `app.py`
```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

### Module Not Found Error
**Solution:** Ensure virtual environment is activated and dependencies installed
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Database Not Created
**Solution:** Run initialization script
```bash
python init_db.py
```

### Can't Login
**Solution:** Reset database and reinitialize
```bash
# Delete database.db file
# Run: python init_db.py
```

---

## 🎨 Customization

### Change Primary Color
Edit `static/css/style.css`:
```css
:root {
    --primary-color: #667eea;      /* Change this color */
    --secondary-color: #764ba2;
}
```

### Change Fine Amount (Rs./day)
Edit `app.py` in `return_book()` function:
```python
fine = max(0, days_late * 10)  # Change 10 to your amount
```

### Change App Title
Edit `base.html`:
```html
<h1>Your App Title Here</h1>
```

---

## 🔐 Security Tips

1. ✅ Change default admin password
2. ✅ Use strong SECRET_KEY in production
3. ✅ Enable HTTPS in production
4. ✅ Keep dependencies updated
5. ✅ Use environment variables for secrets

---

## 📊 Database Schema

### Users Table
- Stores user account information
- Email and username are unique
- Password stored with hash

### Books Table
- Book catalog
- ISBN, publisher, year tracking
- Quantity management

### Borrow History
- Tracks all borrows and returns
- Due date calculation
- Status tracking

### Fines Table
- Calculates late fees
- Tracks payment status

### Activity Log
- Records user actions
- System audit trail

---

## 🚀 Deployment

### For Production:
1. Set `debug=False` in `app.py`
2. Use a proper database (PostgreSQL recommended)
3. Use environment variables for secrets
4. Enable HTTPS
5. Use a production WSGI server (Gunicorn, uWSGI)
6. Set up proper logging
7. Configure CORS if needed

### Example Gunicorn Deployment:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📞 Support

For issues:
1. Check the README.md for detailed documentation
2. Review console error messages
3. Check database initialization
4. Ensure all dependencies are installed

---

## 📝 License

Open source - Free to use and modify

---

**Happy Library Management! 📚**

Last Updated: 2026
