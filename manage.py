#!/usr/bin/env python
import os
import sys
from .env import SessionLocal, init_db, drop_db
from .admin import EventAdmin, PreferenceAdmin
from .models import User

def init():
    """Initialize database"""
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")

def seed():
    """Seed database with sample data"""
    print("Seeding database...")
    db = SessionLocal()
    
    try:
        # Create sample users
        users = [
            User(username="alice", email="alice@example.com", password_hash="hash1"),
            User(username="bob", email="bob@example.com", password_hash="hash2"),
            User(username="charlie", email="charlie@example.com", password_hash="hash3"),
        ]
        db.add_all(users)
        db.commit()
        print(f"✓ Created {len(users)} users")
        
        # Create sample event
        from datetime import datetime, timedelta
        from .models import EventType
        
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(days=7)
        
        event = EventAdmin.create_event(
            db, users[0].id, "Team Offsite", "Annual team meeting",
            "time_based", start, end
        )
        print(f"✓ Created event: {event.title}")
        
    finally:
        db.close()

def drop():
    """Drop all tables"""
    confirm = input("⚠️  This will delete all data. Are you sure? (yes/no): ")
    if confirm.lower() == "yes":
        drop_db()
        print("✓ Database dropped")
    else:
        print("Cancelled")

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if command == "init":
        init()
    elif command == "seed":
        seed()
    elif command == "drop":
        drop()
    else:
        print("""
        Doodle App Management Commands:
        
        python manage.py init    - Initialize database
        python manage.py seed    - Seed with sample data
        python manage.py drop    - Drop all tables
        """)
        