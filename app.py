# Import Flask class from flask package
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# Create Flask application
app = Flask(__name__)

# Configure SQLite database
# Database file will be created in the application directory
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "library.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define Book model
class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(13), unique=True)
    year_published = db.Column(db.Integer)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp)
    
    def __repr__(self):
        return f'<Book {self.title}>'

# Home page route
# When user opens localhost:5000 this function will run
@app.route('/')
def home():
    
    # Render index template
    return render_template('index.html')

# Dashboard page route
# Display library statistics and overview
@app.route('/dashboard')
def dashboard():
    
    # Get all books
    all_books = Book.query.all()
    
    # Calculate statistics
    total_books = len(all_books)
    total_quantity = sum(book.quantity for book in all_books) if all_books else 0
    total_authors = len(set(book.author for book in all_books)) if all_books else 0
    avg_quantity = round(total_quantity / total_books, 1) if total_books > 0 else 0
    
    # Get recent books (last 6)
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(6).all()
    
    # Pass statistics to template
    return render_template('dashboard.html', 
                         total_books=total_books,
                         total_authors=total_authors,
                         total_quantity=total_quantity,
                         avg_quantity=avg_quantity,
                         recent_books=recent_books)

# Books page route
# Display all books in the library
@app.route('/books')
def books():
    
    # Query all books from database
    all_books = Book.query.all()
    
    # Render books template with the list of books
    return render_template('books.html', books=all_books)

# Add book page route
# GET: Display the add book form
# POST: Handle book addition to database
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    
    # If form is submitted (POST request)
    if request.method == 'POST':
        
        # Get form data
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        year_published = request.form.get('year_published')
        quantity = request.form.get('quantity', 1)
        
        # Create new book object
        new_book = Book(
            title=title,
            author=author,
            isbn=isbn if isbn else None,
            year_published=int(year_published) if year_published else None,
            quantity=int(quantity)
        )
        
        # Add book to database
        db.session.add(new_book)
        db.session.commit()
        
        # Redirect to books page after adding
        return redirect(url_for('books'))
    
    # If GET request, display the form
    return render_template('add_book.html')

# Delete book route
# Delete a book from the database by ID
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    
    # Query the book by ID
    book = Book.query.get(book_id)
    
    # If book exists, delete it
    if book:
        db.session.delete(book)
        db.session.commit()
    
    # Redirect back to books page
    return redirect(url_for('books'))

# Main program execution
# This runs only when this file is executed directly
if __name__ == '__main__':
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Start Flask server
    # debug=True automatically reloads server after code changes
    # and shows error messages for developers
    app.run(debug=True)