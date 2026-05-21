# Role-Based Access Control Setup & Testing Guide

## Quick Start

### 1. Start the Application
```bash
python app.py
```
The app will run on `http://127.0.0.1:5000`

---

## Testing the System

### Step 1: Create Test Accounts

#### Create Admin Account (Direct Database)
1. Open Python shell or interactive editor
2. Execute:
```python
from app import app, get_db
from werkzeug.security import generate_password_hash

db = get_db()
db.execute(
    'INSERT INTO users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, ?)',
    ('admin1', 'admin@example.com', generate_password_hash('admin123'), 'Admin User', 'admin')
)
db.commit()
db.close()
```

#### Create Librarian Account
Use the Admin Panel:
1. Login as admin
2. Go to Admin Dashboard
3. Click "Add Librarian"
4. Fill in details and submit

OR directly via database:
```python
db.execute(
    'INSERT INTO users (username, email, password, full_name, role) VALUES (?, ?, ?, ?, ?)',
    ('librarian1', 'lib@example.com', generate_password_hash('lib123'), 'Librarian User', 'librarian')
)
db.commit()
```

#### Create Student Account
1. Go to registration page (`/register`)
2. Fill in all fields
3. Submit (automatically creates with role='user')

---

### Step 2: Test Each Role

#### ADMIN TEST SCENARIOS

**Login:** admin1 / admin123

1. **Dashboard Access**
   - ✅ See system statistics (total books, users, librarians, etc.)
   - ✅ Access all admin controls

2. **Manage Users**
   - ✅ Click "Manage Users"
   - ✅ View all users with pagination
   - ✅ Filter by role (Admin, Librarian, User)
   - ✅ Try to delete a user
   - ❌ Should not be able to delete own account

3. **Add Librarian**
   - ✅ Click "Add Librarian"
   - ✅ Fill in form with unique username/email
   - ✅ Submit and verify librarian appears in user list

4. **View Reports**
   - ✅ Click "Reports"
   - ✅ See borrowing statistics
   - ✅ See overdue books
   - ✅ See fine reports

5. **All Borrowings**
   - ✅ View all borrowing records
   - ✅ Filter by status (Borrowed, Returned)

---

#### LIBRARIAN TEST SCENARIOS

**Login:** librarian1 / lib123

1. **Dashboard Access**
   - ✅ See library statistics (books, available, borrowed, overdue)
   - ✅ See pending overdue books
   - ✅ See recently added books

2. **Add Book**
   - ✅ Click "Add Book"
   - ✅ Fill in required fields: Title, Author, Category, Quantity
   - ✅ Submit and verify book appears in browse

3. **Browse & Edit Books**
   - ✅ Click "Browse Books"
   - ✅ Search by title/author/ISBN
   - ✅ Filter by category
   - ✅ Click edit on a book
   - ✅ Modify details and save

4. **Student Records**
   - ✅ Click "Student Records"
   - ✅ View all students
   - ✅ Search by name/username/email
   - ✅ See their borrowed count and fines

5. **Calculate Fines**
   - ✅ Click "Fines"
   - ✅ Fines auto-calculated for overdue books
   - ✅ Grouped by student
   - ✅ Click "Mark Paid" to settle fine

6. **Issue & Accept Books**
   - ✅ Click "Issue Book"
   - ✅ Select a student (create one if needed)
   - ✅ Choose book and days
   - ✅ Click "Accept Return" to process returns

---

#### STUDENT TEST SCENARIOS

**Register New Account:**
1. Go to `/register`
2. Fill in form (Full Name, Username, Email, Password)
3. Submit

**Login:** with student credentials

1. **Dashboard Access**
   - ✅ See personal statistics (borrowed count, returned count, fines)
   - ✅ See currently borrowed books
   - ✅ See recent history

2. **Browse Books**
   - ✅ Click "Browse Books"
   - ✅ See all available books
   - ✅ Search and filter
   - ❌ Should NOT see Add/Edit/Delete buttons

3. **Borrow Book**
   - ✅ Click "Borrow Book"
   - ✅ See available books (quantity > 0)
   - ✅ Select borrowing period (1-30 days)
   - ✅ Submit and see confirmation
   - ✅ Book appears in "Currently Borrowed"
   - ❌ Cannot borrow same book twice

4. **Return Book**
   - ✅ Click "Return Book"
   - ✅ See borrowed books
   - ✅ Submit return
   - ✅ If overdue, see fine calculated
   - ✅ Book moves to history

5. **View History**
   - ✅ Click "History"
   - ✅ See all past transactions
   - ✅ See status and dates

6. **Profile Settings**
   - ✅ Click "Settings"
   - ✅ Update profile (name, email)
   - ✅ Change password

---

### Step 3: Test Access Control

#### Admin Routes Access
1. **Try accessing as Student:**
   - Go to `/admin/dashboard` as student
   - ❌ Should redirect with warning message

2. **Try accessing as Librarian:**
   - Go to `/admin/add-librarian` as librarian
   - ❌ Should redirect with warning message

#### Librarian Routes Access
1. **Try adding book as Student:**
   - Go to `/add-book` as student
   - ❌ Should redirect with warning message

2. **Try accessing as Admin:**
   - Go to `/librarian/student-records`
   - ✅ Admin access allowed (superuser)

#### Student Routes Access
1. **All authenticated users can:**
   - ✅ Access `/view_books`
   - ✅ Access `/history`
   - ✅ Access `/settings`
   - ✅ Access `/borrow_book`
   - ✅ Access `/return_book`

---

## Troubleshooting

### Issue: "Admin access required" when trying to access admin routes
**Solution:** Make sure your user has role='admin' in the database

### Issue: Navigation menu doesn't show role-specific items
**Solution:** 
- Refresh the page
- Clear browser cache
- Restart the app

### Issue: Cannot delete user
**Possible Reasons:**
- User has active borrowed books
- User is trying to delete themselves
- User doesn't have admin permissions

### Issue: Cannot delete book
**Solution:** First return all borrowed copies, then delete

### Issue: Fine not calculating
**Solution:** 
- Due date must be in the past
- Librarian must visit Calculate Fines page to generate fines
- Click "Calculate Fines" to refresh

---

## Database Verification

### Check User Roles
```sql
SELECT id, username, full_name, role FROM users;
```

### Check Books
```sql
SELECT id, title, author, category, quantity FROM books;
```

### Check Borrow History
```sql
SELECT * FROM borrow_history;
```

### Check Fines
```sql
SELECT * FROM fines WHERE paid = 0;
```

---

## Key Differences Between Roles

| Task | Admin | Librarian | Student |
|------|-------|-----------|---------|
| Add Books | ❌ | ✅ | ❌ |
| Borrow Books | ❌ | ✅ | ✅ |
| View All Users | ✅ | ❌ | ❌ |
| Calculate Fines | ❌ | ✅ | ❌ |
| Access Admin Panel | ✅ | ❌ | ❌ |
| View Student Records | ❌ | ✅ | ❌ |
| See Activity Logs | ✅ | ❌ | ❌ |
| Generate Reports | ✅ | ❌ | ❌ |

---

## Notes

1. **Navigation Updates Dynamically:** Each role sees different menu items
2. **Flash Messages:** Unauthorized access shows clear messages
3. **Activity Logging:** All actions are logged (except for students)
4. **Cascading Permissions:** Librarians can do student tasks, Admins can do everything
5. **Fine Calculation:** Automatic but must visit Fines page to trigger
6. **Book Availability:** Students see only books with quantity > 0

---

## Next Steps

1. Test all features thoroughly
2. Create sample data (books, students)
3. Test borrowing/returning workflow
4. Verify fine calculations
5. Check all access restrictions

For detailed API and feature documentation, see `RBAC_DOCUMENTATION.md`
