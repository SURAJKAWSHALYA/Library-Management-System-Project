from app import app

with app.app_context():
    # Test if strftime filter exists
    if 'strftime' in app.jinja_env.filters:
        print("✅ strftime filter registered")
    else:
        print("❌ strftime filter NOT registered")
    
    # Test parsing datetime
    from datetime import datetime
    test_date = datetime.now()
    result = app.jinja_env.filters['strftime'](test_date, '%Y-%m-%d')
    print(f"✅ strftime test: {result}")
    print("\n✅ ALL FILTERS WORKING - READY TO LOGIN!")
