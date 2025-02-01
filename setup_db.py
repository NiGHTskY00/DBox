from app import app, db  # Import both `app` and `db`

# Create the application context
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")