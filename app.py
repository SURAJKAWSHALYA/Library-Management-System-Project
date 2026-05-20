"""
Library Management System - Flask Backend
Modern Professional Library Management Application
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import sqlite3
import os
from functools import wraps

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== DATETIME FILTER ====================

def parse_datetime(dt_string):
    """Parse SQLite datetime string to Python datetime object"""
    if isinstance(dt_string, str):
        try:
            return datetime.fromisoformat(dt_string)
        except:
            return dt_string
    return dt_string

app.jinja_env.filters['parse_dt'] = parse_datetime

# ==================== DATABASE FUNCTIONS ====================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    db = get_db()
    cursor = db.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Books Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        )
    ''')
    
    # Borrow History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrow_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            return_date TIMESTAMP,
            status TEXT DEFAULT 'borrowed',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')
    
    # Fines Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            borrow_id INTEGER NOT NULL,
            fine_amount REAL DEFAULT 0,
            paid BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (borrow_id) REFERENCES borrow_history(id)
        )
    ''')
    
    # Activity Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    db.commit()
    db.close()

# Initialize database on startup
init_db()

# ==================== AUTHENTICATION FUNCTIONS ====================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        db.close()
        
        if not user or user['role'] != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, action, details=''):
    """Log user activity"""
    db = get_db()
    db.execute(
        'INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)',
        (user_id, action, details)
    )
    db.commit()
    db.close()

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Validation
        if not all([username, email, password, full_name]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
                (username, email, generate_password_hash(password), full_name)
            )
            db.commit()
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
        finally:
            db.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password required', 'danger')
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            log_activity(user['id'], 'Login', f'User {username} logged in')
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    if 'user_id' in session:
        log_activity(session['user_id'], 'Logout', f'User {session["username"]} logged out')
    
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    db = get_db()
    
    # Get statistics
    total_books = db.execute('SELECT COUNT(*) as count FROM books').fetchone()['count']
    total_users = db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    borrowed_books = db.execute('SELECT COUNT(*) as count FROM borrow_history WHERE status = "borrowed"').fetchone()['count']
    total_authors = db.execute('SELECT COUNT(DISTINCT author) as count FROM books').fetchone()['count']
    total_quantity = db.execute('SELECT SUM(quantity) as count FROM books').fetchone()['count'] or 0
    avg_quantity = round(total_quantity / total_books, 2) if total_books > 0 else 0
    
    # Get recently added books
    recent_books = db.execute(
        'SELECT * FROM books ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    
    # Get user's recent activity
    recent_borrows = db.execute(
        '''SELECT b.*, books.title, books.author 
           FROM borrow_history b 
           JOIN books ON b.book_id = books.id 
           WHERE b.user_id = ? 
           ORDER BY b.borrow_date DESC 
           LIMIT 5''',
        (session['user_id'],)
    ).fetchall()
    
    db.close()
    
    return render_template('dashboard.html',
                         total_books=total_books,
                         total_users=total_users,
                         borrowed_books=borrowed_books,
                         total_authors=total_authors,
                         total_quantity=total_quantity,
                         avg_quantity=avg_quantity,
                         recent_books=recent_books,
                         recent_borrows=recent_borrows)

# ==================== BOOK MANAGEMENT ROUTES ====================

@app.route('/books')
@login_required
def view_books():
    """View all books with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    
    db = get_db()
    
    # Build query
    query = 'SELECT * FROM books WHERE 1=1'
    params = []
    
    if search:
        query += ' AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    # Get total count
    count_query = f'SELECT COUNT(*) as count FROM ({query})'
    total_books = db.execute(count_query, params).fetchone()['count']
    
    # Pagination
    per_page = 10
    offset = (page - 1) * per_page
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    books = db.execute(query, params).fetchall()
    
    # Get categories for filter
    categories = db.execute('SELECT DISTINCT category FROM books ORDER BY category').fetchall()
    
    db.close()
    
    total_pages = (total_books + per_page - 1) // per_page
    
    return render_template('books.html',
                         books=books,
                         page=page,
                         total_pages=total_pages,
                         search=search,
                         category=category,
                         categories=categories)

@app.route('/add-book', methods=['GET', 'POST'])
@login_required
def add_book():
    """Add new book"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        quantity = request.form.get('quantity', 0, type=int)
        isbn = request.form.get('isbn', '').strip()
        publisher = request.form.get('publisher', '').strip()
        year = request.form.get('year_published', 0, type=int)
        description = request.form.get('description', '').strip()
        
        # Validation
        if not all([title, author, category, quantity]):
            flash('Title, author, category, and quantity are required', 'danger')
            return redirect(url_for('add_book'))
        
        if quantity < 0:
            flash('Quantity must be positive', 'danger')
            return redirect(url_for('add_book'))
        
        db = get_db()
        try:
            db.execute(
                '''INSERT INTO books (title, author, category, quantity, isbn, publisher, year_published, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (title, author, category, quantity, isbn if isbn else None, publisher, year if year else None, description)
            )
            db.commit()
            log_activity(session['user_id'], 'Add Book', f'Added book: {title}')
            flash('Book added successfully!', 'success')
            return redirect(url_for('view_books'))
        except sqlite3.IntegrityError:
            flash('ISBN already exists', 'danger')
        finally:
            db.close()
    
    return render_template('add_book.html')

@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    """Edit existing book"""
    db = get_db()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        quantity = request.form.get('quantity', 0, type=int)
        isbn = request.form.get('isbn', '').strip()
        publisher = request.form.get('publisher', '').strip()
        year = request.form.get('year_published', 0, type=int)
        description = request.form.get('description', '').strip()
        
        if not all([title, author, category]):
            flash('Title, author, and category are required', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))
        
        try:
            db.execute(
                '''UPDATE books SET title=?, author=?, category=?, quantity=?, isbn=?, publisher=?, year_published=?, description=?
                   WHERE id=?''',
                (title, author, category, quantity, isbn if isbn else None, publisher, year if year else None, description, book_id)
            )
            db.commit()
            log_activity(session['user_id'], 'Edit Book', f'Edited book ID: {book_id}')
            flash('Book updated successfully!', 'success')
            return redirect(url_for('view_books'))
        except sqlite3.IntegrityError:
            flash('ISBN already exists', 'danger')
        finally:
            db.close()
        
        return render_template('edit_book.html', book=None)
    
    # GET request
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    db.close()
    
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('view_books'))
    
    return render_template('edit_book.html', book=book)

@app.route('/delete-book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    """Delete book"""
    db = get_db()
    
    book = db.execute('SELECT title FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if book:
        # Check if book has active borrows
        active_borrows = db.execute(
            'SELECT COUNT(*) as count FROM borrow_history WHERE book_id = ? AND status = "borrowed"',
            (book_id,)
        ).fetchone()['count']
        
        if active_borrows > 0:
            flash('Cannot delete book with active borrows', 'warning')
        else:
            db.execute('DELETE FROM books WHERE id = ?', (book_id,))
            db.commit()
            log_activity(session['user_id'], 'Delete Book', f'Deleted book: {book["title"]}')
            flash('Book deleted successfully!', 'success')
    else:
        flash('Book not found', 'danger')
    
    db.close()
    return redirect(url_for('view_books'))

# ==================== BORROW/RETURN ROUTES ====================

@app.route('/borrow-book', methods=['GET', 'POST'])
@login_required
def borrow_book():
    """Borrow a book"""
    db = get_db()
    
    if request.method == 'POST':
        book_id = request.form.get('book_id', 0, type=int)
        borrow_days = request.form.get('borrow_days', 14, type=int)
        
        # Validate
        if borrow_days < 1 or borrow_days > 30:
            flash('Borrow period must be between 1 and 30 days', 'danger')
            return redirect(url_for('borrow_book'))
        
        # Check book availability
        book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        
        if not book:
            flash('Book not found', 'danger')
            return redirect(url_for('borrow_book'))
        
        if book['quantity'] <= 0:
            flash('Book not available for borrowing', 'warning')
            return redirect(url_for('borrow_book'))
        
        # Check if user already has this book
        existing = db.execute(
            'SELECT COUNT(*) as count FROM borrow_history WHERE user_id = ? AND book_id = ? AND status = "borrowed"',
            (session['user_id'], book_id)
        ).fetchone()['count']
        
        if existing > 0:
            flash('You already have this book. Please return it first', 'warning')
            return redirect(url_for('borrow_book'))
        
        # Create borrow record
        due_date = datetime.now() + timedelta(days=borrow_days)
        
        db.execute(
            '''INSERT INTO borrow_history (user_id, book_id, due_date, status)
               VALUES (?, ?, ?, 'borrowed')''',
            (session['user_id'], book_id, due_date)
        )
        
        # Update book quantity
        db.execute('UPDATE books SET quantity = quantity - 1 WHERE id = ?', (book_id,))
        
        db.commit()
        log_activity(session['user_id'], 'Borrow Book', f'Borrowed book: {book["title"]}')
        flash(f'Book borrowed successfully! Due date: {due_date.strftime("%Y-%m-%d")}', 'success')
        return redirect(url_for('dashboard'))
    
    # GET request - show available books
    books = db.execute('SELECT * FROM books WHERE quantity > 0 ORDER BY title').fetchall()
    db.close()
    
    return render_template('borrow.html', books=books)

@app.route('/return-book', methods=['GET', 'POST'])
@login_required
def return_book():
    """Return a borrowed book"""
    db = get_db()
    
    if request.method == 'POST':
        borrow_id = request.form.get('borrow_id', 0, type=int)
        
        # Get borrow record
        borrow = db.execute(
            'SELECT * FROM borrow_history WHERE id = ? AND user_id = ?',
            (borrow_id, session['user_id'])
        ).fetchone()
        
        if not borrow:
            flash('Borrow record not found', 'danger')
            return redirect(url_for('return_book'))
        
        if borrow['status'] != 'borrowed':
            flash('Book already returned', 'warning')
            return redirect(url_for('return_book'))
        
        # Calculate fine
        due_date = datetime.fromisoformat(borrow['due_date'])
        return_date = datetime.now()
        days_late = (return_date - due_date).days
        fine = max(0, days_late * 10)  # 10 per day fine
        
        # Update borrow record
        db.execute(
            'UPDATE borrow_history SET status = "returned", return_date = ? WHERE id = ?',
            (return_date, borrow_id)
        )
        
        # Add fine if applicable
        if fine > 0:
            db.execute(
                'INSERT INTO fines (user_id, borrow_id, fine_amount) VALUES (?, ?, ?)',
                (session['user_id'], borrow_id, fine)
            )
        
        # Update book quantity
        db.execute(
            'UPDATE books SET quantity = quantity + 1 WHERE id = ?',
            (borrow['book_id'],)
        )
        
        db.commit()
        
        book = db.execute('SELECT title FROM books WHERE id = ?', (borrow['book_id'],)).fetchone()
        log_activity(session['user_id'], 'Return Book', f'Returned book: {book["title"]}')
        
        message = f'Book returned successfully!'
        if fine > 0:
            message += f' Fine: Rs. {fine} (Due to {days_late} days late)'
        
        flash(message, 'success')
        return redirect(url_for('dashboard'))
    
    # GET request - show user's borrowed books
    borrowed = db.execute(
        '''SELECT bh.*, b.title, b.author FROM borrow_history bh
           JOIN books b ON bh.book_id = b.id
           WHERE bh.user_id = ? AND bh.status = "borrowed"
           ORDER BY bh.borrow_date DESC''',
        (session['user_id'],)
    ).fetchall()
    
    db.close()
    
    return render_template('return.html', borrowed=borrowed)

# ==================== HISTORY ROUTES ====================

@app.route('/history')
@login_required
def history():
    """View borrow/return history"""
    page = request.args.get('page', 1, type=int)
    
    db = get_db()
    
    # Get total count
    total = db.execute(
        'SELECT COUNT(*) as count FROM borrow_history WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()['count']
    
    # Pagination
    per_page = 10
    offset = (page - 1) * per_page
    
    history = db.execute(
        '''SELECT bh.*, b.title, b.author, f.fine_amount FROM borrow_history bh
           JOIN books b ON bh.book_id = b.id
           LEFT JOIN fines f ON bh.id = f.borrow_id
           WHERE bh.user_id = ?
           ORDER BY bh.borrow_date DESC
           LIMIT ? OFFSET ?''',
        (session['user_id'], per_page, offset)
    ).fetchall()
    
    db.close()
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('history.html', history=history, page=page, total_pages=total_pages)

# ==================== SETTINGS ROUTES ====================

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings and profile"""
    db = get_db()
    
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            user = db.execute('SELECT password FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            
            if not check_password_hash(user['password'], current_password):
                flash('Current password is incorrect', 'danger')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters', 'danger')
            elif new_password != confirm_password:
                flash('Passwords do not match', 'danger')
            else:
                db.execute(
                    'UPDATE users SET password = ? WHERE id = ?',
                    (generate_password_hash(new_password), session['user_id'])
                )
                db.commit()
                log_activity(session['user_id'], 'Change Password', 'User changed password')
                flash('Password changed successfully!', 'success')
        
        elif action == 'update_profile':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            
            if not full_name or not email:
                flash('Full name and email are required', 'danger')
            else:
                try:
                    db.execute(
                        'UPDATE users SET full_name = ?, email = ? WHERE id = ?',
                        (full_name, email, session['user_id'])
                    )
                    db.commit()
                    session['full_name'] = full_name
                    log_activity(session['user_id'], 'Update Profile', 'User updated profile')
                    flash('Profile updated successfully!', 'success')
                except sqlite3.IntegrityError:
                    flash('Email already exists', 'danger')
    
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()
    
    return render_template('settings.html', user=user)

# ==================== ADMIN ROUTES ====================

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin: Manage users"""
    db = get_db()
    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    db.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Admin: Delete user"""
    if user_id == session['user_id']:
        flash('Cannot delete your own account', 'warning')
        return redirect(url_for('admin_users'))
    
    db = get_db()
    
    # Check if user has active borrows
    active = db.execute(
        'SELECT COUNT(*) as count FROM borrow_history WHERE user_id = ? AND status = "borrowed"',
        (user_id,)
    ).fetchone()['count']
    
    if active > 0:
        flash('Cannot delete user with active borrows', 'warning')
    else:
        # Delete user data
        db.execute('DELETE FROM fines WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM borrow_history WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM activity_log WHERE user_id = ?', (user_id,))
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
        
        log_activity(session['user_id'], 'Delete User', f'Deleted user ID: {user_id}')
        flash('User deleted successfully!', 'success')
    
    db.close()
    return redirect(url_for('admin_users'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_user():
    """Inject user data into all templates"""
    return dict(
        user_id=session.get('user_id'),
        username=session.get('username'),
        full_name=session.get('full_name'),
        role=session.get('role')
    )

# ==================== RUN APP ====================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)