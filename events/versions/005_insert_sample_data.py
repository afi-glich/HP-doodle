"""Insert sample data

Revision ID: 005
Revises: 004
Create Date: 2024-01-05 00:00:00.000000

"""
from alembic import op
from datetime import datetime, timedelta

# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Insert sample users
    op.execute("""
    INSERT INTO users (username, email, password_hash, full_name) VALUES
    ('john_doe', 'john@example.com', 'hash_password_1', 'John Doe'),
    ('jane_smith', 'jane@example.com', 'hash_password_2', 'Jane Smith'),
    ('bob_johnson', 'bob@example.com', 'hash_password_3', 'Bob Johnson'),
    ('alice_williams', 'alice@example.com', 'hash_password_4', 'Alice Williams');
    """)

    # Insert sample events
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    end_date = start_date + timedelta(days=5)
    
    op.execute(f"""
    INSERT INTO events (creator_id, title, description, event_type, start_date, end_date, min_quorum_percentage)
    VALUES 
    (1, 'Team Meeting', 'Quarterly team meeting', 'FULL_DAY', '{start_date}', '{end_date}', 70),
    (1, 'Sprint Planning', 'Sprint planning session', 'TIME_BASED', '{start_date}', '{end_date}', 60);
    """)

    # Insert full-day slots
    op.execute(f"""
    INSERT INTO full_day_slots (event_id, slot_date) VALUES
    (1, '{(start_date + timedelta(days=0)).date()}'),
    (1, '{(start_date + timedelta(days=1)).date()}'),
    (1, '{(start_date + timedelta(days=2)).date()}');
    """)

    # Insert time-based slots
    op.execute(f"""
    INSERT INTO time_based_slots (event_id, start_time, end_time, duration_minutes) VALUES
    (2, '{start_date + timedelta(hours=9)}', '{start_date + timedelta(hours=10)}', 60),
    (2, '{start_date + timedelta(hours=14)}', '{start_date + timedelta(hours=15)}', 60),
    (2, '{start_date + timedelta(days=1, hours=9)}', '{start_date + timedelta(days=1, hours=10)}', 60);
    """)

    # Insert participants
    op.execute("""
    INSERT INTO event_participants (event_id, user_id, status)
    VALUES 
    (1, 2, 'ACCEPTED'),
    (1, 3, 'ACCEPTED'),
    (1, 4, 'ACCEPTED'),
    (2, 2, 'ACCEPTED'),
    (2, 3, 'ACCEPTED'),
    (2, 4, 'ACCEPTED');
    """)

    # Insert sample preferences for full-day event
    op.execute("""
    INSERT INTO full_day_preferences (slot_id, participant_id, preference)
    VALUES
    (1, 1, 'AVAILABLE'),
    (1, 2, 'AVAILABLE'),
    (1, 3, 'MAYBE'),
    (2, 1, 'UNAVAILABLE'),
    (2, 2, 'AVAILABLE'),
    (2, 3, 'AVAILABLE'),
    (3, 1, 'AVAILABLE'),
    (3, 2, 'AVAILABLE'),
    (3, 3, 'AVAILABLE');
    """)

    # Insert sample preferences for time-based event
    op.execute("""
    INSERT INTO time_based_preferences (slot_id, participant_id, preference)
    VALUES
    (1, 4, 'AVAILABLE'),
    (1, 5, 'AVAILABLE'),
    (1, 6, 'UNAVAILABLE'),
    (2, 4, 'AVAILABLE'),
    (2, 5, 'MAYBE'),
    (2, 6, 'AVAILABLE'),
    (3, 4, 'MAYBE'),
    (3, 5, 'AVAILABLE'),
    (3, 6, 'AVAILABLE');
    """)


def downgrade():
    op.execute("DELETE FROM time_based_preferences")
    op.execute("DELETE FROM full_day_preferences")
    op.execute("DELETE FROM event_participants")
    op.execute("DELETE FROM time_based_slots")
    op.execute("DELETE FROM full_day_slots")
    op.execute("DELETE FROM events")
    op.execute("DELETE FROM users")
