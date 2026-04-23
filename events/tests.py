from django.test import TestCase

# Create your tests here.
import pytest
from datetime import datetime, timedelta
from .env import SessionLocal, drop_db, init_db
from .models import Base, User, Event, TimeSlot, Participant, Preference, EventType, PreferenceStatus
from .views import EventService

@pytest.fixture
def db():
    """Create test database"""
    init_db()
    db = SessionLocal()
    yield db
    db.close()
    drop_db()

def test_create_user(db):
    """Test user creation"""
    user = User(username="testuser", email="test@example.com", password_hash="hash")
    db.add(user)
    db.commit()
    
    retrieved = db.query(User).filter(User.username == "testuser").first()
    assert retrieved.email == "test@example.com"

def test_create_event(db):
    """Test event creation"""
    creator = User(username="creator", email="creator@example.com", password_hash="hash")
    db.add(creator)
    db.commit()
    
    start = datetime.now()
    end = start + timedelta(days=7)
    
    event = Event(
        title="Team Meeting",
        description="Quarterly sync",
        creator_id=creator.id,
        event_type=EventType.TIME_BASED,
        start_date=start,
        end_date=end
    )
    db.add(event)
    db.commit()
    
    retrieved = db.query(Event).filter(Event.title == "Team Meeting").first()
    assert retrieved.creator_id == creator.id

def test_add_time_slots(db):
    """Test adding time slots"""
    creator = User(username="creator", email="creator@example.com", password_hash="hash")
    db.add(creator)
    db.commit()
    
    start = datetime.now()
    end = start + timedelta(days=7)
    
    event = Event(
        title="Meeting",
        creator_id=creator.id,
        event_type=EventType.TIME_BASED,
        start_date=start,
        end_date=end
    )
    db.add(event)
    db.commit()
    
    slot = TimeSlot(
        event_id=event.id,
        slot_date=start.date(),
        start_time=start.time(),
        end_time=(start + timedelta(hours=1)).time()
    )
    db.add(slot)
    db.commit()
    
    assert len(event.time_slots) == 1

def test_preference_workflow(db):
    """Test complete preference workflow"""
    # Create users
    creator = User(username="creator", email="creator@example.com", password_hash="hash")
    participant = User(username="participant", email="part@example.com", password_hash="hash")
    db.add_all([creator, participant])
    db.commit()
    
    # Create event
    start = datetime.now()
    end = start + timedelta(days=7)
    
    event = Event(
        title="Planning",
        creator_id=creator.id,
        event_type=EventType.TIME_BASED,
        start_date=start,
        end_date=end
    )
    db.add(event)
    db.commit()
    
    # Add time slot
    slot = TimeSlot(
        event_id=event.id,
        slot_date=start.date(),
        start_time=start.time(),
        end_time=(start + timedelta(hours=1)).time()
    )
    db.add(slot)
    db.commit()
    
    # Invite participant
    part = Participant(event_id=event.id, user_id=participant.id)
    db.add(part)
    db.commit()
    
    # Set preference
    pref = Preference(
        event_id=event.id,
        user_id=participant.id,
        time_slot_id=slot.id,
        status=PreferenceStatus.AVAILABLE
    )
    db.add(pref)
    db.commit()
    
    assert slot.preferences[0].status == PreferenceStatus.AVAILABLE

def test_best_slot_calculation(db):
    """Test best slot calculation"""
    creator = User(username="creator", email="creator@example.com", password_hash="hash")
    users = [User(username=f"user{i}", email=f"u{i}@example.com", password_hash="hash") 
             for i in range(3)]
    db.add_all([creator] + users)
    db.commit()
    
    start = datetime.now()
    event = Event(
        title="Meeting",
        creator_id=creator.id,
        event_type=EventType.TIME_BASED,
        start_date=start,
        end_date=start + timedelta(days=7)
    )
    db.add(event)
    db.commit()
    
    # Create 2 slots
    slot1 = TimeSlot(event_id=event.id, slot_date=start.date(), start_time=start.time())
    slot2 = TimeSlot(event_id=event.id, slot_date=(start + timedelta(days=1)).date(), 
                     start_time=start.time())
    db.add_all([slot1, slot2])
    db.commit()
    
    # Add participants
    for user in users:
        part = Participant(event_id=event.id, user_id=user.id)
        db.add(part)
    db.commit()
    
    # Slot1: 2 available, 1 maybe
    Preference(event_id=event.id, user_id=users[0].id, time_slot_id=slot1.id, 
               status=PreferenceStatus.AVAILABLE).save()
    Preference(event_id=event.id, user_id=users[1].id, time_slot_id=slot1.id, 
               status=PreferenceStatus.AVAILABLE).save()
    Preference(event_id=event.id, user_id=users[2].id, time_slot_id=slot1.id, 
               status=PreferenceStatus.MAYBE).save()
    
    # Slot2: 1 available
    Preference(event_id=event.id, user_id=users[0].id, time_slot_id=slot2.id, 
               status=PreferenceStatus.AVAILABLE).save()
    
    db.commit()
    
    # Best slot should be slot1
    from .admin import PreferenceAdmin
    best = PreferenceAdmin.calculate_best_slot(db, event.id)
    assert best.id == slot1.id