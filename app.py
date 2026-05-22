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

def datetime_to_timestamp(dt):
    """Convert datetime to timestamp"""
    if isinstance(dt, str):
        dt = parse_datetime(dt)
    if isinstance(dt, datetime):
        return int(dt.timestamp())
    return int(dt)

def get_current_datetime():
    """Get current datetime"""
    return datetime.now()

def format_datetime(value, format_string='%Y-%m-%d %H:%M:%S'):
    """Format datetime to string"""
    if isinstance(value, str):
        value = parse_datetime(value)
    if isinstance(value, datetime):
        return value.strftime(format_string)
    return value

app.jinja_env.filters['parse_dt'] = parse_datetime
app.jinja_env.filters['as_timestamp'] = datetime_to_timestamp
app.jinja_env.filters['strftime'] = format_datetime
app.jinja_env.globals['now'] = get_current_datetime()

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
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'borrowed',
            return_verified INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')

    # Ensure older databases get the new borrow_history columns
    cursor.execute('PRAGMA table_info(borrow_history)')
    existing_columns = [row[1] for row in cursor.fetchall()]
    if 'quantity' not in existing_columns:
        cursor.execute('ALTER TABLE borrow_history ADD COLUMN quantity INTEGER DEFAULT 1')
    if 'return_verified' not in existing_columns:
        cursor.execute('ALTER TABLE borrow_history ADD COLUMN return_verified INTEGER DEFAULT 0')
    
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

def librarian_required(f):
    """Decorator to require librarian role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        db.close()
        
        if not user or user['role'] != 'librarian':
            flash('Librarian access required', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Decorator to require student/user role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        db.close()
        
        if not user or user['role'] not in ['user', 'student']:
            flash('Student access required', 'danger')
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
    """Main dashboard - shows different content based on user role"""
    role = session.get('role', 'user')
    db = get_db()
    
    # Route to role-specific dashboard
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'librarian':
        return redirect(url_for('librarian_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin Dashboard - System overview and administration"""
    db = get_db()
    
    # Get statistics
    total_books = db.execute('SELECT COUNT(*) as count FROM books').fetchone()['count']
    total_users = db.execute('SELECT COUNT(*) as count FROM users WHERE role IN ("user", "student")').fetchone()['count']
    total_librarians = db.execute('SELECT COUNT(*) as count FROM users WHERE role = "librarian"').fetchone()['count']
    total_admins = db.execute('SELECT COUNT(*) as count FROM users WHERE role = "admin"').fetchone()['count']
    borrowed_books = db.execute('SELECT COUNT(*) as count FROM borrow_history WHERE status = "borrowed"').fetchone()['count']
    total_quantity = db.execute('SELECT SUM(quantity) as count FROM books').fetchone()['count'] or 0
    
    # Get pending fines
    pending_fines = db.execute('SELECT COUNT(*) as count FROM fines WHERE paid = 0').fetchone()['count']
    total_fines = db.execute('SELECT SUM(fine_amount) as total FROM fines WHERE paid = 0').fetchone()['total'] or 0
    
    # Get categories
    categories = db.execute('SELECT DISTINCT category FROM books ORDER BY category').fetchall()
    
    # Get recent activity
    recent_activity = db.execute('''
        SELECT al.*, u.full_name FROM activity_log al
        JOIN users u ON al.user_id = u.id
        ORDER BY al.created_at DESC LIMIT 10
    ''').fetchall()
    
    db.close()
    
    return render_template('admin/dashboard.html',
                         total_books=total_books,
                         total_users=total_users,
                         total_librarians=total_librarians,
                         total_admins=total_admins,
                         borrowed_books=borrowed_books,
                         total_quantity=total_quantity,
                         pending_fines=pending_fines,
                         total_fines=total_fines,
                         categories=categories,
                         recent_activity=recent_activity)

@app.route('/librarian/dashboard')
@librarian_required
def librarian_dashboard():
    """Librarian Dashboard - Book operations and management"""
    db = get_db()
    
    # Get statistics
    total_books = db.execute('SELECT COUNT(*) as count FROM books').fetchone()['count']
    available_books = db.execute('SELECT COUNT(*) as count FROM books WHERE quantity > 0').fetchone()['count']
    borrowed_books = db.execute('SELECT COUNT(*) as count FROM borrow_history WHERE status = "borrowed"').fetchone()['count']
    overdue_books = db.execute('''
        SELECT COUNT(*) as count FROM borrow_history 
        WHERE status = "borrowed" AND due_date < CURRENT_TIMESTAMP
    ''').fetchone()['count']
    
    # Get pending requests
    pending_requests = db.execute('''
        SELECT bh.*, b.title, b.author, u.full_name FROM borrow_history bh
        JOIN books b ON bh.book_id = b.id
        JOIN users u ON bh.user_id = u.id
        WHERE bh.status = "requested"
        ORDER BY bh.borrow_date ASC LIMIT 5
    ''').fetchall()

    # Get pending returns
    pending_returns = db.execute('''
        SELECT bh.*, b.title, u.full_name FROM borrow_history bh
        JOIN books b ON bh.book_id = b.id
        JOIN users u ON bh.user_id = u.id
        WHERE bh.status = "borrowed" AND bh.due_date < CURRENT_TIMESTAMP
        ORDER BY bh.due_date ASC LIMIT 5
    ''').fetchall()
    
    # Get recently added books
    recent_books = db.execute('''
        SELECT * FROM books ORDER BY created_at DESC LIMIT 5
    ''').fetchall()
    
    # Get categories
    categories = db.execute('SELECT DISTINCT category FROM books ORDER BY category').fetchall()
    
    db.close()
    
    return render_template('librarian/dashboard.html',
                         total_books=total_books,
                         available_books=available_books,
                         borrowed_books=borrowed_books,
                         overdue_books=overdue_books,
                         pending_requests=pending_requests,
                         pending_returns=pending_returns,
                         recent_books=recent_books,
                         categories=categories)

@app.route('/librarian/borrow-requests')
@librarian_required
def librarian_borrow_requests():
    """View and manage pending borrower requests"""
    db = get_db()
    requests = db.execute('''
        SELECT bh.*, b.title, b.author, u.full_name FROM borrow_history bh
        JOIN books b ON bh.book_id = b.id
        JOIN users u ON bh.user_id = u.id
        WHERE bh.status = "requested"
        ORDER BY bh.borrow_date ASC
    ''').fetchall()

    available_books = db.execute('SELECT * FROM books WHERE quantity > 0 ORDER BY title').fetchall()
    db.close()
    return render_template('librarian/borrow_requests.html', requests=requests, available_books=available_books)

@app.route('/librarian/approve-request/<int:request_id>', methods=['POST'])
@librarian_required
def approve_request(request_id):
    db = get_db()
    request_row = db.execute('SELECT * FROM borrow_history WHERE id = ? AND status = "requested"', (request_id,)).fetchone()
    if not request_row:
        db.close()
        flash('Request not found or already processed', 'danger')
        return redirect(url_for('librarian_borrow_requests'))

    book = db.execute('SELECT * FROM books WHERE id = ?', (request_row['book_id'],)).fetchone()
    request_quantity = request_row['quantity'] or 1
    if not book or book['quantity'] < request_quantity:
        db.close()
        flash('Book is not available in the requested quantity to issue', 'warning')
        return redirect(url_for('librarian_borrow_requests'))

    db.execute('UPDATE borrow_history SET status = "borrowed" WHERE id = ?', (request_id,))
    db.execute('UPDATE books SET quantity = quantity - ? WHERE id = ?', (request_quantity, book['id']))
    db.commit()
    db.close()
    log_activity(session['user_id'], 'Approve Request', f'Approved request ID: {request_id} for {request_quantity} copy(ies) of {book["title"]}')
    flash('Request approved and book issued', 'success')
    return redirect(url_for('librarian_borrow_requests'))

@app.route('/librarian/decline-request/<int:request_id>', methods=['POST'])
@librarian_required
def decline_request(request_id):
    db = get_db()
    request_row = db.execute('SELECT bh.*, b.title FROM borrow_history bh JOIN books b ON bh.book_id = b.id WHERE bh.id = ? AND bh.status = "requested"', (request_id,)).fetchone()
    if not request_row:
        db.close()
        flash('Request not found or already processed', 'danger')
        return redirect(url_for('librarian_borrow_requests'))

    db.execute('DELETE FROM borrow_history WHERE id = ?', (request_id,))
    db.commit()
    db.close()
    log_activity(session['user_id'], 'Decline Request', f'Declined book request ID: {request_id} for {request_row["title"]}')
    flash('Request declined successfully', 'info')
    return redirect(url_for('librarian_borrow_requests'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student/User Dashboard - Personal library activities"""
    db = get_db()
    
    # Get user statistics
    borrowed_count = db.execute(
        'SELECT COUNT(*) as count FROM borrow_history WHERE user_id = ? AND status = "borrowed"',
        (session['user_id'],)
    ).fetchone()['count']
    
    returned_count = db.execute(
        'SELECT COUNT(*) as count FROM borrow_history WHERE user_id = ? AND status = "returned"',
        (session['user_id'],)
    ).fetchone()['count']
    
    # Get pending fines
    pending_fines = db.execute(
        'SELECT COUNT(*) as count FROM fines WHERE user_id = ? AND paid = 0',
        (session['user_id'],)
    ).fetchone()['count']
    
    total_fine_amount = db.execute(
        'SELECT SUM(fine_amount) as total FROM fines WHERE user_id = ? AND paid = 0',
        (session['user_id'],)
    ).fetchone()['total'] or 0
    
    # Get currently borrowed books
    borrowed_books = db.execute('''
        SELECT bh.*, b.title, b.author, b.cover_image
        FROM borrow_history bh
        JOIN books b ON bh.book_id = b.id
        WHERE bh.user_id = ? AND bh.status = "borrowed"
        ORDER BY bh.due_date ASC
    ''', (session['user_id'],)).fetchall()
    
    # Get recent history
    recent_history = db.execute('''
        SELECT bh.*, b.title, b.author
        FROM borrow_history bh
        JOIN books b ON bh.book_id = b.id
        WHERE bh.user_id = ?
        ORDER BY bh.borrow_date DESC LIMIT 5
    ''', (session['user_id'],)).fetchall()
    
    db.close()
    
    return render_template('student/dashboard.html',
                         borrowed_count=borrowed_count,
                         returned_count=returned_count,
                         pending_fines=pending_fines,
                         total_fine_amount=total_fine_amount,
                         borrowed_books=borrowed_books,
                         recent_history=recent_history)

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

    role = session.get('role', 'user')
    requested_book_ids = []
    if role in ['user', 'student']:
        requested_rows = db.execute(
            'SELECT book_id FROM borrow_history WHERE user_id = ? AND status IN ("requested", "borrowed")',
            (session['user_id'],)
        ).fetchall()
        requested_book_ids = [row['book_id'] for row in requested_rows]
    
    db.close()
    
    total_pages = (total_books + per_page - 1) // per_page
    
    return render_template('books.html',
                         books=books,
                         page=page,
                         total_pages=total_pages,
                         search=search,
                         category=category,
                         categories=categories,
                         role=role,
                         requested_book_ids=requested_book_ids)

@app.route('/request-book', methods=['POST'])
@student_required
def request_book():
    """Student requests a book for librarian approval"""
    book_id = request.form.get('book_id', 0, type=int)
    borrow_days = request.form.get('borrow_days', 14, type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    if borrow_days < 1 or borrow_days > 30:
        flash('Request period must be between 1 and 30 days', 'danger')
        return redirect(url_for('view_books'))
    
    if quantity < 1:
        flash('Please request at least one copy', 'danger')
        return redirect(url_for('view_books'))

    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    if not book:
        db.close()
        flash('Book not found', 'danger')
        return redirect(url_for('view_books'))
    
    if quantity > book['quantity']:
        db.close()
        flash(f'Only {book["quantity"]} copies are available right now', 'warning')
        return redirect(url_for('view_books'))

    existing = db.execute(
        'SELECT COUNT(*) as count FROM borrow_history WHERE user_id = ? AND book_id = ? AND status IN ("requested", "borrowed")',
        (session['user_id'], book_id)
    ).fetchone()['count']
    
    if existing > 0:
        db.close()
        flash('You have already requested or borrowed this book', 'warning')
        return redirect(url_for('view_books'))
    
    due_date = datetime.now() + timedelta(days=borrow_days)
    db.execute(
        'INSERT INTO borrow_history (user_id, book_id, due_date, quantity, status) VALUES (?, ?, ?, ?, "requested")',
        (session['user_id'], book_id, due_date, quantity)
    )
    db.commit()
    db.close()
    log_activity(session['user_id'], 'Request Book', f'Requested {quantity} copy(ies) of: {book["title"]}')
    flash('Your request has been submitted to the librarian', 'success')
    return redirect(url_for('view_books'))

@app.route('/add-book', methods=['GET', 'POST'])
@librarian_required
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
@librarian_required
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
@librarian_required
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
@librarian_required
def borrow_book():
    """Redirect issue-book view to combined borrow requests page"""
    if request.method == 'POST':
        db = get_db()
        book_id = request.form.get('book_id', 0, type=int)
        borrow_days = request.form.get('borrow_days', 14, type=int)
        
        # Validate
        if borrow_days < 1 or borrow_days > 30:
            flash('Borrow period must be between 1 and 30 days', 'danger')
            return redirect(url_for('borrow_book'))
        
        # Check book availability
        book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        
        if not book:
            db.close()
            flash('Book not found', 'danger')
            return redirect(url_for('borrow_book'))
        
        if book['quantity'] <= 0:
            db.close()
            flash('Book not available for borrowing', 'warning')
            return redirect(url_for('borrow_book'))
        
        # Check if user already has this book
        existing = db.execute(
            'SELECT COUNT(*) as count FROM borrow_history WHERE user_id = ? AND book_id = ? AND status = "borrowed"',
            (session['user_id'], book_id)
        ).fetchone()['count']
        
        if existing > 0:
            db.close()
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
        db.close()
        log_activity(session['user_id'], 'Borrow Book', f'Borrowed book: {book["title"]}')
        flash(f'Book borrowed successfully! Due date: {due_date.strftime("%Y-%m-%d")}', 'success')
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('librarian_borrow_requests'))

@app.route('/return-book', methods=['GET', 'POST'])
@librarian_required
def return_book():
    """Return a borrowed book"""
    db = get_db()
    
    if request.method == 'POST':
        borrow_id = request.form.get('borrow_id', 0, type=int)
        
        # Get borrow record
        borrow = db.execute(
            'SELECT * FROM borrow_history WHERE id = ? AND status = "borrowed"',
            (borrow_id,)
        ).fetchone()
        
        if not borrow:
            flash('Borrow record not found or book already returned', 'danger')
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
                (borrow['user_id'], borrow_id, fine)
            )
        
        # Update book quantity
        db.execute(
            'UPDATE books SET quantity = quantity + ? WHERE id = ?',
            (borrow['quantity'] or 1, borrow['book_id'])
        )
        
        db.commit()
        
        book = db.execute('SELECT title FROM books WHERE id = ?', (borrow['book_id'],)).fetchone()
        quantity = borrow['quantity'] or 1
        log_activity(session['user_id'], 'Return Book', f'Returned {quantity} copy(ies) of {book["title"]}')
        
        message = f'Book returned successfully!'
        if quantity > 1:
            message = f'{quantity} copies returned successfully!'
        if fine > 0:
            message += f' Fine: Rs. {fine} (Due to {days_late} days late)'
        
        flash(message, 'success')
        return redirect(url_for('dashboard'))
    
    # GET request - show all borrowed books pending return
    borrowed = db.execute(
        '''SELECT bh.*, b.title, b.author, u.full_name FROM borrow_history bh
           JOIN books b ON bh.book_id = b.id
           JOIN users u ON bh.user_id = u.id
           WHERE bh.status = "borrowed"
           ORDER BY bh.borrow_date DESC'''
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
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '').strip()
    
    db = get_db()
    
    # Build query
    query = 'SELECT * FROM users WHERE 1=1'
    params = []
    
    if role_filter:
        query += ' AND role = ?'
        params.append(role_filter)
    
    # Get total count
    count_query = f'SELECT COUNT(*) as count FROM ({query})'
    total_users = db.execute(count_query, params).fetchone()['count']
    
    # Pagination
    per_page = 10
    offset = (page - 1) * per_page
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    users = db.execute(query, params).fetchall()
    db.close()
    
    total_pages = (total_users + per_page - 1) // per_page
    
    return render_template('admin/users.html',
                         users=users,
                         page=page,
                         total_pages=total_pages,
                         role_filter=role_filter)

@app.route('/admin/add-librarian', methods=['GET', 'POST'])
@admin_required
def add_librarian():
    """Admin: Add librarian"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Validation
        if not all([username, email, password, full_name]):
            flash('All fields are required', 'danger')
            return redirect(url_for('add_librarian'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('add_librarian'))
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, "librarian")',
                (username, email, generate_password_hash(password), full_name)
            )
            db.commit()
            log_activity(session['user_id'], 'Add Librarian', f'Added librarian: {full_name}')
            flash('Librarian added successfully!', 'success')
            return redirect(url_for('admin_users'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
        finally:
            db.close()
    
    return render_template('admin/add_librarian.html')

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
        user = db.execute('SELECT full_name FROM users WHERE id = ?', (user_id,)).fetchone()
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
        
        log_activity(session['user_id'], 'Delete User', f'Deleted user: {user["full_name"]}')
        flash('User deleted successfully!', 'success')
    
    db.close()
    return redirect(url_for('admin_users'))

@app.route('/admin/manage-categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    """Admin: Manage book categories"""
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'add':
            category = request.form.get('category', '').strip()
            
            if not category:
                flash('Category name is required', 'danger')
                return redirect(url_for('manage_categories'))
            
            db = get_db()
            # Check if category already exists
            existing = db.execute('SELECT COUNT(*) as count FROM books WHERE category = ?', (category,)).fetchone()['count']
            
            if existing > 0:
                flash('Category already exists', 'warning')
            else:
                # Add a placeholder book to create the category (or just store in settings later)
                flash('You can use this category when adding books', 'success')
            db.close()
    
    db = get_db()
    categories = db.execute('SELECT DISTINCT category FROM books ORDER BY category').fetchall()
    db.close()
    
    return render_template('admin/manage_categories.html', categories=categories)

@app.route('/admin/reports')
@admin_required
def admin_reports():
    """Admin: View reports"""
    db = get_db()
    
    # Borrowing Report
    borrowing_report = db.execute('''
        SELECT b.title, COUNT(*) as times_borrowed
        FROM borrow_history bh
        JOIN books b ON bh.book_id = b.id
        GROUP BY bh.book_id
        ORDER BY times_borrowed DESC
        LIMIT 10
    ''').fetchall()
    
    # User Activity Report
    user_activity = db.execute('''
        SELECT u.full_name, COUNT(*) as activities
        FROM activity_log al
        JOIN users u ON al.user_id = u.id
        GROUP BY al.user_id
        ORDER BY activities DESC
        LIMIT 10
    ''').fetchall()
    
    # Overdue Report
    overdue_report = db.execute('''
        SELECT u.full_name, b.title, bh.due_date
        FROM borrow_history bh
        JOIN users u ON bh.user_id = u.id
        JOIN books b ON bh.book_id = b.id
        WHERE bh.status = "borrowed" AND bh.due_date < CURRENT_TIMESTAMP
        ORDER BY bh.due_date ASC
    ''').fetchall()
    
    # Fine Report
    fine_report = db.execute('''
        SELECT u.full_name, SUM(fine_amount) as total_fines, COUNT(*) as fine_count
        FROM fines f
        JOIN users u ON f.user_id = u.id
        GROUP BY f.user_id
        ORDER BY total_fines DESC
    ''').fetchall()
    
    db.close()
    
    return render_template('admin/reports.html',
                         borrowing_report=borrowing_report,
                         user_activity=user_activity,
                         overdue_report=overdue_report,
                         fine_report=fine_report)

@app.route('/admin/all-borrowed-books')
@admin_required
def admin_borrowed_books():
    """Admin: View all borrowed books"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'borrowed').strip()
    
    db = get_db()
    
    # Build query
    query = 'SELECT bh.*, b.title, b.author, u.full_name FROM borrow_history bh JOIN books b ON bh.book_id = b.id JOIN users u ON bh.user_id = u.id WHERE 1=1'
    params = []
    
    if status_filter in ['borrowed', 'returned']:
        query += ' AND bh.status = ?'
        params.append(status_filter)
    
    # Get total count
    count_query = f'SELECT COUNT(*) as count FROM ({query})'
    total = db.execute(count_query, params).fetchone()['count']
    
    # Pagination
    per_page = 10
    offset = (page - 1) * per_page
    query += ' ORDER BY bh.borrow_date DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    borrowed_books = db.execute(query, params).fetchall()
    db.close()
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('admin/borrowed_books.html',
                         borrowed_books=borrowed_books,
                         page=page,
                         total_pages=total_pages,
                         status_filter=status_filter)

@app.route('/admin/verify-return/<int:borrow_id>', methods=['POST'])
@admin_required
def admin_verify_return(borrow_id):
    db = get_db()
    borrow = db.execute('SELECT * FROM borrow_history WHERE id = ? AND status = "returned"', (borrow_id,)).fetchone()
    if not borrow:
        db.close()
        flash('Return record not found or not yet returned', 'danger')
        return redirect(url_for('admin_borrowed_books'))

    db.execute('UPDATE borrow_history SET return_verified = 1 WHERE id = ?', (borrow_id,))
    db.commit()
    db.close()
    log_activity(session['user_id'], 'Verify Return', f'Verified return for borrow ID: {borrow_id}')
    flash('Return has been verified successfully', 'success')
    return redirect(url_for('admin_borrowed_books'))

# ==================== LIBRARIAN ROUTES ====================

@app.route('/librarian/student-records')
@librarian_required
def student_records():
    """Librarian: View all student records"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    db = get_db()
    
    # Build query
    query = 'SELECT * FROM users WHERE role IN ("user", "student")'
    params = []
    
    if search:
        query += ' AND (full_name LIKE ? OR username LIKE ? OR email LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])
    
    # Get total count
    count_query = f'SELECT COUNT(*) as count FROM ({query})'
    total = db.execute(count_query, params).fetchone()['count']
    
    # Pagination
    per_page = 10
    offset = (page - 1) * per_page
    query += ' ORDER BY full_name ASC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    students = db.execute(query, params).fetchall()
    
    # Get additional info for each student
    student_info = []
    for student in students:
        borrowed = db.execute(
            'SELECT COUNT(*) as count FROM borrow_history WHERE user_id = ? AND status = "borrowed"',
            (student['id'],)
        ).fetchone()['count']
        
        fines = db.execute(
            'SELECT SUM(fine_amount) as total FROM fines WHERE user_id = ? AND paid = 0',
            (student['id'],)
        ).fetchone()['total'] or 0
        
        student_info.append({
            'student': student,
            'borrowed_count': borrowed,
            'fines': fines
        })
    
    db.close()
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('librarian/student_records.html',
                         student_info=student_info,
                         page=page,
                         total_pages=total_pages,
                         search=search)

@app.route('/librarian/calculate-fines')
@librarian_required
def calculate_fines():
    """Librarian: Calculate and manage fines"""
    db = get_db()
    
    # Get all overdue books with pending fines
    overdue_fines = db.execute('''
        SELECT bh.*, b.title, u.full_name, u.email,
               CAST((julianday(CURRENT_TIMESTAMP) - julianday(bh.due_date)) AS INTEGER) as days_overdue
        FROM borrow_history bh
        JOIN books b ON bh.book_id = b.id
        JOIN users u ON bh.user_id = u.id
        WHERE bh.status = "borrowed" AND bh.due_date < CURRENT_TIMESTAMP
        ORDER BY bh.due_date ASC
    ''').fetchall()
    
    # Calculate fines for all overdue books
    for fine_record in overdue_fines:
        days_overdue = max(1, fine_record['days_overdue'])
        fine_amount = days_overdue * 10  # 10 per day
        
        # Check if fine already exists
        existing_fine = db.execute(
            'SELECT COUNT(*) as count FROM fines WHERE borrow_id = ?',
            (fine_record['id'],)
        ).fetchone()['count']
        
        if existing_fine == 0:
            db.execute(
                'INSERT INTO fines (user_id, borrow_id, fine_amount) VALUES (?, ?, ?)',
                (fine_record['user_id'], fine_record['id'], fine_amount)
            )
    
    db.commit()
    
    # Get updated fine records
    all_fines = db.execute('''
        SELECT f.*, u.full_name, b.title, bh.due_date
        FROM fines f
        JOIN users u ON f.user_id = u.id
        JOIN borrow_history bh ON f.borrow_id = bh.id
        JOIN books b ON bh.book_id = b.id
        WHERE f.paid = 0
        ORDER BY f.created_at DESC
    ''').fetchall()
    
    # Group by user
    fines_by_user = {}
    for fine in all_fines:
        user_id = fine['user_id']
        if user_id not in fines_by_user:
            fines_by_user[user_id] = {
                'user_name': fine['full_name'],
                'fines': [],
                'total': 0
            }
        fines_by_user[user_id]['fines'].append(fine)
        fines_by_user[user_id]['total'] += fine['fine_amount']
    
    db.close()
    
    return render_template('librarian/calculate_fines.html',
                         fines_by_user=fines_by_user)

@app.route('/librarian/mark-fine-paid/<int:fine_id>', methods=['POST'])
@librarian_required
def mark_fine_paid(fine_id):
    """Librarian: Mark fine as paid"""
    db = get_db()
    
    fine = db.execute('SELECT * FROM fines WHERE id = ?', (fine_id,)).fetchone()
    
    if fine:
        db.execute('UPDATE fines SET paid = 1 WHERE id = ?', (fine_id,))
        db.commit()
        log_activity(session['user_id'], 'Mark Fine Paid', f'Marked fine {fine_id} as paid')
        flash(f'Fine marked as paid: Rs. {fine["fine_amount"]}', 'success')
    else:
        flash('Fine record not found', 'danger')
    
    db.close()
    return redirect(url_for('calculate_fines'))

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