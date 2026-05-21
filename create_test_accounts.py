"""Create test accounts for Admin and Librarian"""
from app import app, get_db
from werkzeug.security import generate_password_hash

def create_test_accounts():
    with app.app_context():
        db = get_db()
        
        # Create admin account
        try:
            db.execute(
                'INSERT INTO users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, ?)',
                ('admin', 'admin@library.com', generate_password_hash('admin123'), 'Administrator', 'admin')
            )
            print("✅ Admin account created")
        except Exception as e:
            print(f"⚠️ Admin account: {e}")
        
        # Create librarian account
        try:
            db.execute(
                'INSERT INTO users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, ?)',
                ('librarian', 'librarian@library.com', generate_password_hash('librarian123'), 'Librarian Staff', 'librarian')
            )
            print("✅ Librarian account created")
        except Exception as e:
            print(f"⚠️ Librarian account: {e}")
        
        db.commit()
        db.close()
        
        print("\n" + "="*60)
        print("✅ TEST ACCOUNTS READY")
        print("="*60)
        print("\n📝 LOGIN CREDENTIALS:\n")
        print("ADMIN:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nLIBRARIAN:")
        print("  Username: librarian")
        print("  Password: librarian123")
        print("\nSTUDENT:")
        print("  Register via /register page")
        print("\n" + "="*60)

if __name__ == '__main__':
    create_test_accounts()
