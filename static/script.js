/* ==============================
   Library Management System - JavaScript
   ============================== */

// ==============================
// Document Ready
// ==============================
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// ==============================
// Initialize Application
// ==============================
function initializeApp() {
    // Add event listeners to form elements
    setupFormValidation();
    setupBookSearch();
    setupSmoothScroll();
    setupAnimations();
    setupDeleteFunctionality();
    setupDashboardAnimations();
    setupThemeToggle();
}

// ==============================
// Delete Functionality
// ==============================
function setupDeleteFunctionality() {
    const deleteForms = document.querySelectorAll('.delete-form');
    
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Prevent default form submission
            // The confirmation happens via the button's onclick handler
        });
    });
}

// ==============================
// Confirm Delete
// ==============================
function confirmDelete(bookTitle) {
    const confirmed = confirm(`Are you sure you want to delete "${bookTitle}"? This action cannot be undone.`);
    
    if (confirmed) {
        showSuccess(`Deleting "${bookTitle}"...`);
    }
    
    return confirmed;
}

// ==============================
// Form Validation
// ==============================
function setupFormValidation() {
    const bookForm = document.querySelector('.book-form');
    
    if (bookForm) {
        bookForm.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showError('Please fill in all required fields correctly.');
            } else {
                showSuccess('Adding book to library...');
            }
        });

        // Real-time validation
        const titleInput = document.getElementById('title');
        const authorInput = document.getElementById('author');
        const isbnInput = document.getElementById('isbn');
        const quantityInput = document.getElementById('quantity');

        if (titleInput) {
            titleInput.addEventListener('blur', function() {
                if (this.value.trim().length < 1) {
                    this.classList.add('input-error');
                } else {
                    this.classList.remove('input-error');
                }
            });
        }

        if (authorInput) {
            authorInput.addEventListener('blur', function() {
                if (this.value.trim().length < 1) {
                    this.classList.add('input-error');
                } else {
                    this.classList.remove('input-error');
                }
            });
        }

        if (isbnInput) {
            isbnInput.addEventListener('input', function() {
                // Only allow numbers
                this.value = this.value.replace(/\D/g, '').slice(0, 13);
            });

            isbnInput.addEventListener('blur', function() {
                if (this.value && (this.value.length !== 13 && this.value.length !== 10)) {
                    this.classList.add('input-error');
                } else {
                    this.classList.remove('input-error');
                }
            });
        }

        if (quantityInput) {
            quantityInput.addEventListener('change', function() {
                if (this.value < 1) {
                    this.value = 1;
                }
            });
        }
    }
}

// ==============================
// Validate Form
// ==============================
function validateForm(form) {
    const title = form.querySelector('#title');
    const author = form.querySelector('#author');
    const quantity = form.querySelector('#quantity');

    // Check required fields
    if (!title || !title.value.trim()) {
        return false;
    }

    if (!author || !author.value.trim()) {
        return false;
    }

    if (!quantity || quantity.value < 1) {
        return false;
    }

    // Validate ISBN if provided
    const isbn = form.querySelector('#isbn');
    if (isbn && isbn.value) {
        if (isbn.value.length !== 13 && isbn.value.length !== 10) {
            return false;
        }
    }

    return true;
}

// ==============================
// Book Search/Filter
// ==============================
function setupBookSearch() {
    const table = document.querySelector('table');
    
    if (table) {
        // Create search box if it doesn't exist
        const bookSection = document.querySelector('.books-section');
        if (bookSection) {
            const searchBox = document.createElement('div');
            searchBox.className = 'search-box';
            searchBox.innerHTML = `
                <input 
                    type="text" 
                    id="search-input" 
                    class="form-control" 
                    placeholder="🔍 Search books by title, author, or ISBN..."
                    style="margin-bottom: 20px;"
                >
            `;
            
            // Insert search box before the table
            const tableContainer = table.parentElement;
            tableContainer.insertBefore(searchBox, table);

            // Add search functionality
            const searchInput = document.getElementById('search-input');
            searchInput.addEventListener('keyup', filterTable);
        }
    }
}

// ==============================
// Filter Table
// ==============================
function filterTable(e) {
    const searchTerm = e.target.value.toLowerCase();
    const table = document.querySelector('table');
    const rows = table.querySelectorAll('tbody tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
            row.classList.add('fade-in');
        } else {
            row.style.display = 'none';
        }
    });

    // Show no results message if all rows are hidden
    const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
    if (visibleRows.length === 0) {
        console.log('No books match your search');
    }
}

// ==============================
// Smooth Scroll
// ==============================
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ==============================
// Animations
// ==============================
function setupAnimations() {
    // Animate cards on page load
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Animate table rows on page load
    const rows = document.querySelectorAll('table tbody tr');
    rows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            row.style.transition = 'all 0.3s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateX(0)';
        }, index * 50);
    });
}

// ==============================
// Show Success Message
// ==============================
function showSuccess(message) {
    createNotification(message, 'success');
}

// ==============================
// Show Error Message
// ==============================
function showError(message) {
    createNotification(message, 'error');
}

// ==============================
// Create Notification
// ==============================
function createNotification(message, type) {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 5px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        max-width: 400px;
        word-wrap: break-word;
    `;

    if (type === 'success') {
        notification.style.backgroundColor = '#48bb78';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#f56565';
    }

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ==============================
// Utility: Format Date
// ==============================
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ==============================
// Utility: Count Books
// ==============================
function countBooks() {
    const rows = document.querySelectorAll('table tbody tr');
    return rows.length;
}

// ==============================
// Utility: Sort Table
// ==============================
function sortTable(columnIndex, isNumeric = false) {
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();

        if (isNumeric) {
            return parseInt(aValue) - parseInt(bValue);
        } else {
            return aValue.localeCompare(bValue);
        }
    });

    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// ==============================
// Add Animation Keyframes
// ==============================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
 
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    .fade-in {
        animation: fadeIn 0.3s ease;
    }

    .input-error {
        border-color: #f56565 !important;
        background-color: #fff5f5 !important;
    }

    .notification {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
`;
document.head.appendChild(style);

// ==============================
// Dashboard Animations
// ==============================
function setupDashboardAnimations() {
    // Animate stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Animate action cards
    const actionCards = document.querySelectorAll('.action-card');
    actionCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'scale(0.9)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'scale(1)';
        }, index * 150 + 300);
    });

    // Animate book cards
    const bookCards = document.querySelectorAll('.book-card');
    bookCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50 + 500);
    });

    // Animate info cards
    const infoCards = document.querySelectorAll('.info-card');
    infoCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateX(-20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateX(0)';
        }, index * 100 + 700);
    });
}

// ==============================
// Theme Toggle - Dark Mode
// ==============================
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    if (!themeToggle) return;
    
    // Get saved theme from localStorage, default to 'light'
    const savedTheme = localStorage.getItem('bs-theme') || 'light';
    body.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    // Theme toggle button click
    themeToggle.addEventListener('click', function() {
        const currentTheme = body.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        // Update theme
        body.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('bs-theme', newTheme);
        
        // Update icon
        updateThemeIcon(newTheme);
        
        // Show notification
        showThemeNotification(newTheme);
    });
}

// ==============================
// Update Theme Icon
// ==============================
function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const icon = themeToggle.querySelector('i');
    if (theme === 'dark') {
        icon.classList.remove('bi-moon-fill');
        icon.classList.add('bi-sun-fill');
        themeToggle.title = 'Switch to Light Mode';
    } else {
        icon.classList.remove('bi-sun-fill');
        icon.classList.add('bi-moon-fill');
        themeToggle.title = 'Switch to Dark Mode';
    }
}

// ==============================
// Show Theme Notification
// ==============================
function showThemeNotification(theme) {
    const message = theme === 'dark' ? '🌙 Dark Mode Enabled' : '☀️ Light Mode Enabled';
    createNotification(message, 'success');
}

// ==============================
// Console Messages
// ==============================
console.log('%c📚 Library Management System', 'color: #667eea; font-size: 20px; font-weight: bold;');
console.log('%cApplication loaded successfully!', 'color: #48bb78; font-size: 14px;');
