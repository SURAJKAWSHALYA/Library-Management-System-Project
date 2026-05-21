# Role-Based Access Control System - Documentation

## Overview
The Library Management System now features a comprehensive role-based access control system with three distinct user roles:
1. **Admin** - System Administration
2. **Librarian** - Library Operations
3. **Student/User** - Library Member

---

## 1. ADMIN PANEL

### Access & Requirements
- **Decorator:** `@admin_required`
- **Route:** `/admin/dashboard`
- **Default Role Value:** `'admin'`

### Admin Features

#### 1.1 Dashboard (`/admin/dashboard`)
- **Statistics Overview:**
  - Total books in library
  - Total users, librarians, and admins
  - Currently borrowed books
  - Pending fines count and total amount
  - Available books in stock

- **System Controls:**
  - Manage Users
  - Add Librarians
  - Manage Categories
  - View Reports
  - View All Borrowings
  
- **Recent Activity Log:** Last 10 system activities

#### 1.2 Manage Users (`/admin/users`)
- **Features:**
  - View all users with pagination
  - Filter by role (Admin, Librarian, User, Student)
  - Delete users (except those with active borrows)
  - View user details (name, email, role, join date)
  
- **Restrictions:**
  - Cannot delete own account
  - Cannot delete users with active borrowed books

#### 1.3 Add Librarian (`/admin/add-librarian`)
- **Create librarian accounts with:**
  - Full name
  - Username (unique)
  - Email (unique)
  - Password (min 6 characters)
  
- **Automatically sets role:** `'librarian'`

#### 1.4 Manage Categories (`/admin/manage-categories`)
- View all book categories currently in use
- Add new categories
- Categories are auto-created when books are added

#### 1.5 View Reports (`/admin/reports`)
- **Top 10 Most Borrowed Books** - Borrowing frequency analysis
- **Top 10 Active Users** - User activity metrics
- **Overdue Books Report** - Books not returned on time with details
- **Pending Fines Report** - All outstanding fines by user

#### 1.6 All Borrowed Books (`/admin/all-borrowed-books`)
- View all borrowing records with pagination
- Filter by status (Borrowed, Returned, All)
- See student name, book title, dates, and current status
- Highlight overdue books

---

## 2. LIBRARIAN PANEL

### Access & Requirements
- **Decorator:** `@librarian_required` (Librarian or Admin can access)
- **Route:** `/librarian/dashboard`
- **Default Role Value:** `'librarian'`

### Librarian Features

#### 2.1 Dashboard (`/librarian/dashboard`)
- **Statistics:**
  - Total books in library
  - Available books (quantity > 0)
  - Currently borrowed books
  - Overdue books count
  
- **Pending Actions:**
  - List of overdue books with student names
  - Due dates
  - Days overdue
  
- **Recently Added Books:** Last 5 books with edit/delete options

#### 2.2 Browse Books (`/view_books`)
- Search and filter books
- **Can perform:**
  - Add new books
  - Edit book details
  - Delete books (if no active borrows)
  
- **Search Options:**
  - By title, author, ISBN
  - Filter by category

#### 2.3 Add Book (`/add-book`)
- **Required Fields:**
  - Title
  - Author
  - Category
  - Quantity
  
- **Optional Fields:**
  - ISBN
  - Publisher
  - Year published
  - Description

#### 2.4 Student Records (`/librarian/student-records`)
- **View all students with:**
  - Name, username, email
  - Currently borrowed book count
  - Pending fines amount
  - Join date
  
- **Search:** By name, username, or email
- **Pagination:** 10 students per page

#### 2.5 Calculate Fines (`/librarian/calculate-fines`)
- **Automatically calculates fines:**
  - Fine rate: Rs. 10 per day overdue
  - Grouped by student
  - Shows total fines per student
  
- **Mark Fine as Paid:** 
  - Click to mark fines as settled
  - Records payment in system

#### 2.6 Issue Book (`/borrow-book`)
- Search and select available books
- Set borrow period (1-30 days)
- Updates book quantity automatically

#### 2.7 Accept Return (`/return-book`)
- View student's borrowed books
- Process returns
- Automatically calculate fines if overdue
- Update book quantity

---

## 3. STUDENT/USER PANEL

### Access & Requirements
- **Decorator:** `@student_required` (accepts 'user' or 'student')
- **Route:** `/student/dashboard`
- **Default Role Values:** `'user'` or `'student'`

### Student Features

#### 3.1 Dashboard (`/student/dashboard`)
- **Personal Statistics:**
  - Currently borrowed books
  - Total returned books
  - Pending fines count and amount
  
- **Quick Actions:**
  - Browse Books
  - Borrow Book
  - Return Book
  - View History
  
- **Currently Borrowed Books Section:**
  - Book title and author
  - Borrow date
  - Due date (highlighted if overdue)
  - Option to return
  
- **Recent Borrowing History:**
  - Last 5 transactions
  - Book details
  - Status (Borrowed/Returned)

#### 3.2 Browse Books (`/view_books`)
- Search all available books
- Filter by category
- View book details
- **Cannot:**
  - Add books
  - Edit books
  - Delete books

#### 3.3 Borrow Book (`/borrow-book`)
- Browse available books
- Select borrow period
- Request to borrow
- **Restrictions:**
  - Cannot borrow same book twice (if already borrowed)
  - Book must be available (quantity > 0)

#### 3.4 Return Book (`/return-book`)
- View currently borrowed books
- Submit return request
- Fines calculated automatically
- Receive confirmation

#### 3.5 View History (`/history`)
- Complete borrowing/returning history
- Paginated (10 per page)
- Shows dates and status
- Fine amount if applicable

#### 3.6 Profile Settings (`/settings`)
- Update full name and email
- Change password
- View account information

---

## Database Structure

### Users Table - Role Field
```
role: TEXT
- 'admin'     → Administrator
- 'librarian' → Library Staff
- 'user'      → Library Member
- 'student'   → Library Member (alternative)
```

---

## Route Protection Summary

### Admin-Only Routes
```
/admin/dashboard              - Admin Dashboard
/admin/users                  - Manage Users
/admin/add-librarian          - Add Librarian
/admin/delete-user/<id>       - Delete User
/admin/manage-categories      - Manage Categories
/admin/reports                - View Reports
/admin/all-borrowed-books     - View All Borrowings
```

### Librarian Routes (Librarian + Admin)
```
/add-book                     - Add Book
/edit-book/<id>               - Edit Book
/delete-book/<id>             - Delete Book
/librarian/dashboard          - Librarian Dashboard
/librarian/student-records    - View Student Records
/librarian/calculate-fines    - Calculate Fines
/librarian/mark-fine-paid/<id>- Mark Fine as Paid
```

### Student Routes
```
/student/dashboard            - Student Dashboard
/borrow-book                  - Borrow Book
/return-book                  - Return Book
/history                      - View History
/settings                     - Profile Settings
```

---

## Navigation Menu Structure

The sidebar navigation dynamically changes based on user role:

### For Admin Users
- Dashboard
- **Admin Panel**
  - Manage Users
  - Add Librarian
  - Categories
  - Reports
  - All Borrowings
- Settings
- Logout

### For Librarian Users
- Dashboard
- **Librarian Panel**
  - Browse Books
  - Add Book
  - Student Records
  - Fines
  - Issue Book
  - Accept Return
- Settings
- Logout

### For Student Users
- Dashboard
- **Student Panel**
  - Browse Books
  - Borrow Book
  - Return Book
  - History
- Settings
- Logout

---

## Key Features by Role

| Feature | Admin | Librarian | Student |
|---------|-------|-----------|---------|
| View Dashboard | ✅ | ✅ | ✅ |
| Search Books | ✅ | ✅ | ✅ |
| Add Books | ❌ | ✅ | ❌ |
| Edit Books | ❌ | ✅ | ❌ |
| Delete Books | ❌ | ✅ | ❌ |
| Borrow Books | ❌ | ✅ | ✅ |
| Return Books | ❌ | ✅ | ✅ |
| View Fines | ✅ | ✅ | ✅ |
| Calculate Fines | ❌ | ✅ | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| Add Librarians | ✅ | ❌ | ❌ |
| View Reports | ✅ | ❌ | ❌ |
| View Activity Log | ✅ | ❌ | ❌ |

---

## Registration & Initial Setup

### Default Registration
New users register with role: `'user'` or `'student'`

### Admin Setup
To create admin accounts:
1. Use Flask shell or direct database access
2. Set role to `'admin'` in users table

### Librarian Creation
Admins can create librarian accounts via:
- Admin Panel → Add Librarian button
- OR `/admin/add-librarian` form

---

## Security Considerations

1. **Login Required:** All protected routes require authentication
2. **Role Verification:** System checks role on each request
3. **Data Protection:** Users can only access their own data (except Admin/Librarian)
4. **Deletion Restrictions:** Cannot delete accounts with active borrows
5. **Self-Protection:** Users cannot delete their own accounts

---

## Error Handling

- **Unauthorized Access:** Redirects to dashboard with warning
- **Missing Data:** Flash messages indicate required fields
- **Duplicate Entries:** Username/Email validation prevents duplicates
- **Invalid Operations:** Cannot delete books with active borrows

---

## Templates Organization

```
templates/
├── base.html                           (Navigation updated)
├── admin/
│   ├── dashboard.html                  (Admin Dashboard)
│   ├── users.html                      (Manage Users)
│   ├── add_librarian.html              (Add Librarian Form)
│   ├── manage_categories.html          (Category Management)
│   ├── reports.html                    (System Reports)
│   └── borrowed_books.html             (All Borrowing Records)
├── librarian/
│   ├── dashboard.html                  (Librarian Dashboard)
│   ├── student_records.html            (Student Records)
│   └── calculate_fines.html            (Fine Management)
└── student/
    └── dashboard.html                  (Student Dashboard)
```

---

## Testing Checklist

- [ ] Admin can access admin dashboard
- [ ] Librarian can access librarian dashboard
- [ ] Student can access student dashboard
- [ ] Admin can add/delete librarians
- [ ] Admin can manage users
- [ ] Librarian can add/edit/delete books
- [ ] Librarian can view student records
- [ ] Librarian can calculate fines
- [ ] Student can borrow books
- [ ] Student can return books
- [ ] Fine calculation is automatic
- [ ] Navigation shows correct menu for each role
- [ ] Unauthorized access is blocked
- [ ] Books with active borrows cannot be deleted
- [ ] Users with active borrows cannot be deleted
