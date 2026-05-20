#!/usr/bin/env python
"""
Library Management System - Setup and Initialization Script
This script initializes the database and creates a default admin user
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'database.db'

def init_db():
    """Initialize database"""
    db = sqlite3.connect(DATABASE)
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
    print("✅ Database initialized successfully!")

def create_admin_user():
    """Create a default admin user"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    try:
        admin_password = generate_password_hash('admin123')
        cursor.execute(
            '''INSERT INTO users (username, email, password, full_name, role)
               VALUES (?, ?, ?, ?, ?)''',
            ('admin', 'admin@library.com', admin_password, 'Administrator', 'admin')
        )
        db.commit()
        print("✅ Admin user created!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  Please change this password after first login!")
    except sqlite3.IntegrityError:
        print("ℹ️  Admin user already exists")
    finally:
        db.close()

def add_sample_books():
    """Add sample books to the database"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    sample_books = [
        ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 5, '978-0743273565', 'Scribner', 1925, 'A classic American novel'),
        ('To Kill a Mockingbird', 'Harper Lee', 'Fiction', 3, '978-0061120084', 'J.B. Lippincott & Co.', 1960, 'Classic tale of racial injustice'),
        ('1984', 'George Orwell', 'Fiction', 4, '978-0451524935', 'Secker & Warburg', 1949, 'Dystopian novel'),
        ('Pride and Prejudice', 'Jane Austen', 'Fiction', 2, '978-0141439518', 'Penguin', 1813, 'Romantic novel'),
        ('The Catcher in the Rye', 'J.D. Salinger', 'Fiction', 6, '978-0316769174', 'Little, Brown', 1951, 'Coming of age novel'),
        ('A Brief History of Time', 'Stephen Hawking', 'Science', 3, '978-0553380163', 'Bantam Dell', 1988, 'Popular science book'),
        ('Sapiens', 'Yuval Noah Harari', 'Non-Fiction', 4, '978-0062316097', 'Harper', 2014, 'History of humankind'),
        ('The Art of War', 'Sun Tzu', 'Strategy', 2, '978-0143039999', 'Penguin', 1994, 'Ancient military strategy'),
    ]
    
    try:
        for book in sample_books:
            cursor.execute(
                '''INSERT INTO books (title, author, category, quantity, isbn, publisher, year_published, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                book
            )
        db.commit()
        print(f"✅ Added {len(sample_books)} sample books!")
    except sqlite3.IntegrityError:
        print("ℹ️  Sample books already exist")
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("=" * 60)
    print("Library Management System - Initialization")
    print("=" * 60)
    
    # Initialize database
    if not os.path.exists(DATABASE):
        print("\n📦 Creating database...")
        init_db()
    else:
        print("\n✅ Database already exists")
        init_db()
    
    print("\n👤 Setting up admin user...")
    create_admin_user()
    
    print("\n📚 Adding sample books...")
    add_sample_books()
    
    print("\n" + "=" * 60)
    print("✅ Initialization complete!")
    print("\nTo run the application:")
    print("  python app.py")
    print("\nAccess at: http://localhost:5000")
    print("=" * 60)

if __name__ == '__main__':
    main()
