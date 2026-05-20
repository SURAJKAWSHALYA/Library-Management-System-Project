# Configuration Reference

## Flask Configuration

```python
# app.py Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Run Configuration
app.run(debug=True, host='127.0.0.1', port=5000)
```

## Database Configuration

- **Type**: SQLite3
- **File**: `database.db`
- **Auto-creation**: Yes (on first run)
- **Tables**: 5 (users, books, borrow_history, fines, activity_log)

## Customizable Settings

### 1. Fine Amount (Rs./day)
**File**: `app.py`
**Function**: `return_book()`
**Line**: `fine = max(0, days_late * 10)`
**Change**: Replace `10` with desired amount

### 2. Borrow Period Limits
**File**: `app.py`
**Function**: `borrow_book()`
**Validation**: `1-30 days`
**Change**: Update validation logic

### 3. Pagination Size
**File**: `app.py`
**Variable**: `per_page = 10`
**Change**: Update in relevant functions

### 4. Session Timeout
**File**: `app.py`
**Config**: Add `PERMANENT_SESSION_LIFETIME`
**Example**: `app.permanent_session_lifetime = timedelta(hours=24)`

### 5. Primary Colors
**File**: `static/css/style.css`
**CSS Variables**:
```css
--primary-color: #667eea;
--secondary-color: #764ba2;
--success-color: #43e97b;
--danger-color: #f5576c;
--info-color: #4facfe;
```

## Environment Variables (for production)

Create `.env` file:
```
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=production
DATABASE_URL=sqlite:///database.db
DEBUG=False
```

## Deployment Configuration

### Development
```python
app.run(debug=True, port=5000)
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Production with Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Security Configuration

### For Production:
1. Set `debug=False`
2. Change `SECRET_KEY`
3. Use HTTPS/SSL
4. Set secure cookie flags
5. Enable CORS if needed
6. Use environment variables
7. Set up logging
8. Enable rate limiting
9. Use strong database password
10. Regular security updates

## Template Configuration

### To Add New Menu Item in Sidebar:
**File**: `templates/base.html`
**Location**: `<ul class="nav-menu">`
**Add**:
```html
<li class="nav-item">
    <a href="{{ url_for('your_route') }}" class="nav-link">
        <i class="fas fa-icon"></i>
        <span>Label</span>
    </a>
</li>
```

### To Add New Dashboard Card:
**File**: `templates/dashboard.html`
**Add**:
```html
<div class="col-md-3 col-sm-6 mb-3">
    <div class="stat-card">
        <!-- Card content -->
    </div>
</div>
```

## Email Configuration (for future)

To add email notifications:
```python
# Add to requirements.txt
Flask-Mail==0.9.1

# Add to app.py
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
```

## Logging Configuration (for debugging)

Add to `app.py`:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/library_app.log',
                                       maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Library Management System started')
```

## API Rate Limiting (for future)

To add rate limiting:
```bash
pip install Flask-Limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/data')
@limiter.limit("10 per minute")
def api_data():
    return jsonify({'data': 'value'})
```

## CORS Configuration (for API)

```bash
pip install Flask-CORS
```

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

## Caching Configuration

Add to `app.py`:
```bash
pip install Flask-Caching
```

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/books')
@cache.cached(timeout=300)
def view_books():
    # Cached for 5 minutes
    pass
```

## Database Backup

Create backup script:
```python
import shutil
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/database_{timestamp}.db"
    shutil.copy('database.db', backup_file)
    print(f"Backup created: {backup_file}")

if __name__ == '__main__':
    backup_database()
```

## Performance Optimization

### Database Query Optimization:
- Add indexes on frequently searched columns
- Use pagination for large datasets
- Cache frequently accessed data

### Frontend Optimization:
- Minify CSS/JS in production
- Use CDN for static files
- Lazy load images
- Enable gzip compression

### Nginx Compression:
```nginx
gzip on;
gzip_types text/plain text/css text/xml 
            text/javascript application/x-javascript
            application/xml+rss application/javascript;
gzip_min_length 256;
```

---

This configuration file provides reference for customization and deployment.
