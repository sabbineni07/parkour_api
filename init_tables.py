#!/usr/bin/env python3
"""
Script to initialize database tables.
This can be run manually or as part of the startup process.
"""
import sys
import time
from app import create_app, db
from app.models.user import User
from app.models.dataset import Dataset

def wait_for_db(max_retries=30, delay=1):
    """Wait for database to be ready"""
    app = create_app()
    with app.app_context():
        for i in range(max_retries):
            try:
                # Try to connect to the database
                db.engine.connect()
                print("✓ Database connection successful!")
                return True
            except Exception as e:
                if i < max_retries - 1:
                    print(f"Waiting for database... (attempt {i+1}/{max_retries})")
                    time.sleep(delay)
                else:
                    print(f"✗ Failed to connect to database after {max_retries} attempts")
                    print(f"Error: {e}")
                    return False
    return False

def init_tables():
    """Create all database tables"""
    app = create_app()
    with app.app_context():
        try:
            print("Creating database tables...")
            db.create_all()
            print("✓ Database tables created successfully!")
            
            # Create admin user if it doesn't exist
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@parkour.com',
                    first_name='Admin',
                    last_name='User'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created: username=admin, password=admin123")
            else:
                print("✓ Admin user already exists")
            
            return True
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 50)
    print("Initializing Parkour API Database")
    print("=" * 50)
    
    if not wait_for_db():
        sys.exit(1)
    
    if not init_tables():
        sys.exit(1)
    
    print("=" * 50)
    print("Database initialization complete!")
    print("=" * 50)


