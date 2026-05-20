# Library Management System

A modern, professional Library Management System built with Flask, SQLite, HTML5, CSS3, and JavaScript with a beautiful glassmorphism UI design.

## Features

### 1. Authentication System
- ✅ User Registration
- ✅ User Login with Session Management
- ✅ Password Hashing (Werkzeug Security)
- ✅ Logout Functionality
- ✅ Flash Messages
- ✅ Redirect After Login

### 2. Dashboard
- ✅ Modern Admin Dashboard
- ✅ Real-time Statistics
  - Total Books Count
  - Total Users Count
  - Books Borrowed Count
  - Recently Added Books
- ✅ Quick Action Buttons
- ✅ User Activity Overview
- ✅ Responsive Layout

### 3. Book Management
- ✅ Add Books
  - Title, Author, Category
  - ISBN, Publisher, Year
  - Quantity, Description
- ✅ View Books
  - Pagination (10 per page)
  - Search by Title/Author/ISBN
  - Filter by Category
  - Responsive Table
- ✅ Edit Books
  - Update all book details
  - Prefilled forms
  - Validation
- ✅ Delete Books
  - Confirmation popup
  - Prevent deletion if books are borrowed

### 4. Borrow Book System
- ✅ Select Book
- ✅ Set Borrow Period (1-30 days)
- ✅ Automatic Quantity Reduction
- ✅ Prevent Duplicate Borrowing
- ✅ Due Date Calculation
- ✅ Borrow History

### 5. Return Book System
- ✅ Return Borrowed Books
- ✅ Automatic Quantity Increment
- ✅ Fine Calculation
  - Rs. 10 per day late fee
- ✅ Return Status Tracking
- ✅ Return History

### 6. User Management
- ✅ User List (Admin Only)
- ✅ User Deletion
- ✅ User Activity Log
- ✅ Role-based Access (Admin/User)

### 7. History & Activity
- ✅ Borrow History with Pagination
- ✅ Return History
- ✅ Activity Logging
- ✅ Fine Tracking

### 8. Settings & Profile
- ✅ Update Profile Information
- ✅ Change Password
- ✅ Password Validation
- ✅ Email Updates

## UI/UX Features

### Design Elements
- ✅ Dark Blue & Black Theme
- ✅ Glassmorphism Cards
- ✅ Smooth Animations
- ✅ Beautiful Buttons & Forms
- ✅ Professional Typography
- ✅ Responsive Tables
- ✅ Modern Login Page
- ✅ Attractive Dashboard

### Responsive Design
- ✅ Mobile Friendly
- ✅ Tablet Compatible
- ✅ Desktop Optimized
- ✅ Sidebar Navigation
- ✅ Mobile Menu Toggle
- ✅ Flexible Grid Layout

### Interactive Features
- ✅ Loading Animations
- ✅ Scroll Effects
- ✅ Hover Effects
- ✅ Form Validation
- ✅ Search Filters
- ✅ Pagination
- ✅ Modal Dialogs

## Project Structure

```
Library-Management-System/
│
├── app.py                          # Main Flask application
├── database.db                     # SQLite database
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── templates/                      # HTML Templates
│   ├── base.html                   # Base template with navbar & sidebar
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   ├── dashboard.html              # Main dashboard
│   ├── books.html                  # Books listing
│   ├── add_book.html               # Add book form
│   ├── edit_book.html              # Edit book form
│   ├── borrow.html                 # Borrow book form
│   ├── return.html                 # Return book form
│   ├── history.html                # Borrow/return history
│   ├── settings.html               # User settings
│   ├── admin_users.html            # Admin user management
│   ├── 404.html                    # 404 error page
│   └── 500.html                    # 500 error page
│
├── static/                         # Static files
│   ├── css/
│   │   ├── style.css               # Main stylesheet
│   │   └── auth.css                # Authentication pages style
│   ├── js/
│   │   └── script.js               # JavaScript functionality
│   └── images/                     # Image assets
│
└── .gitignore                      # Git ignore file
```

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Security**: Werkzeug (Password Hashing)

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual Environment (recommended)

### Step 1: Clone or Download the Project
```bash
cd "Library Management System"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 5: Access the Application
- Open your web browser
- Go to `http://127.0.0.1:5000`
- You'll be redirected to login page

## Default Credentials

The system initializes with no default users. You need to register first.

### To Create an Admin User:
1. Register a new account
2. Update database directly (or use Django admin/Flask-Admin)
3. Change `role` field to `'admin'`

```sql
UPDATE users SET role = 'admin' WHERE id = 1;
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Books Table
```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    isbn TEXT UNIQUE,
    publisher TEXT,
    year_published INTEGER,
    description TEXT,
    cover_image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Borrow History Table
```sql
CREATE TABLE borrow_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    return_date TIMESTAMP,
    status TEXT DEFAULT 'borrowed',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

### Fines Table
```sql
CREATE TABLE fines (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    borrow_id INTEGER NOT NULL,
    fine_amount REAL DEFAULT 0,
    paid BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (borrow_id) REFERENCES borrow_history(id)
);
```

### Activity Log Table
```sql
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Usage Guide

### For Regular Users

1. **Register Account**
   - Click "Register here"
   - Fill in all required fields
   - Password must be at least 6 characters

2. **Browse Books**
   - Navigate to "View Books"
   - Use search to find books
   - Filter by category

3. **Borrow Books**
   - Click "Borrow Book"
   - Select a book from available list
   - Choose borrow period (1-30 days)
   - Submit

4. **Return Books**
   - Click "Return Book"
   - Select book to return
   - Fine will be calculated if late
   - Confirm return

5. **View History**
   - Click "History"
   - View all your borrow/return records
   - Track fines and due dates

### For Admin Users

1. **Manage Books**
   - Add new books
   - Edit existing books
   - Delete books (if not borrowed)
   - Search and filter

2. **Manage Users**
   - View all users
   - Delete user accounts
   - View user activity

3. **View Statistics**
   - Dashboard shows system overview
   - Track total books, users, borrows

## API Endpoints

### Authentication
- `GET /` - Home (redirects to login if not authenticated)
- `POST /register` - Register new user
- `POST /login` - Login user
- `GET /logout` - Logout user

### Dashboard
- `GET /dashboard` - Main dashboard (requires login)

### Books
- `GET /books` - View all books with search/filter (requires login)
- `GET /add-book` - Add book form (requires login)
- `POST /add-book` - Submit add book form (requires login)
- `GET /edit-book/<id>` - Edit book form (requires login)
- `POST /edit-book/<id>` - Submit edit book form (requires login)
- `POST /delete-book/<id>` - Delete book (requires login)

### Borrow/Return
- `GET /borrow-book` - Borrow book form (requires login)
- `POST /borrow-book` - Submit borrow (requires login)
- `GET /return-book` - Return book form (requires login)
- `POST /return-book` - Submit return (requires login)

### History & Settings
- `GET /history` - View history (requires login)
- `GET /settings` - User settings (requires login)
- `POST /settings` - Update settings (requires login)

### Admin
- `GET /admin/users` - Manage users (requires admin)
- `POST /admin/delete-user/<id>` - Delete user (requires admin)

## Features in Detail

### Search Functionality
- Real-time search by title, author, or ISBN
- Category filtering
- Pagination support
- No results message

### Borrow System
- Check availability before borrowing
- Prevent duplicate borrowing
- Automatic due date calculation
- Fine calculation (Rs. 10/day)
- Quantity tracking

### Security Features
- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection ready
- SQL injection prevention
- Admin-only endpoints

### Form Validation
- Required field validation
- Email format validation
- Password strength validation
- Password confirmation
- Quantity validation

## Customization

### Change Dark Theme Color
Edit `static/css/style.css`:
```css
:root {
    --primary-color: #667eea;      /* Change this */
    --secondary-color: #764ba2;    /* Change this */
    ...
}
```

### Change Fine Amount
Edit `app.py` in `return_book()` function:
```python
fine = max(0, days_late * 10)  # Change 10 to desired amount
```

### Change Session Secret Key
Edit `app.py`:
```python
app.config['SECRET_KEY'] = 'your-new-secret-key'
```

## Troubleshooting

### Database Issues
- Delete `database.db` to reset
- Run `python app.py` to recreate

### Port Already in Use
- Change port in `app.py`:
  ```python
  app.run(debug=True, host='127.0.0.1', port=5001)
  ```

### Module Not Found
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### CORS Issues
- Add CORS headers in Flask if needed
- Install Flask-CORS: `pip install flask-cors`

## Performance Optimization

- Database indexes on common queries
- Pagination for large datasets
- Lazy loading for images
- CSS/JS minification recommended
- Database connection pooling

## Future Enhancements

- [ ] Email notifications for due dates
- [ ] PDF report generation
- [ ] Advanced analytics dashboard
- [ ] Book recommendations
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] Mobile app
- [ ] Payment integration for fines
- [ ] Book ratings and reviews
- [ ] Wishlist functionality

## Security Considerations

- Change SECRET_KEY for production
- Use HTTPS in production
- Enable CSRF protection
- Validate all inputs
- Use environment variables for secrets
- Implement rate limiting
- Add logging and monitoring
- Regular security updates

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions:
1. Check the troubleshooting section
2. Review the code comments
3. Refer to Flask documentation

## Version

Current Version: 1.0.0
Last Updated: 2026

## Author

Created with ❤️ using Flask

---

**Happy Library Management!** 📚
