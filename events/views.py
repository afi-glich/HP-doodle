from django.shortcuts import render

from sqlalchemy.orm import Session
from .models import Event, User, Participant, Preference, TimeSlot, PreferenceStatus
from .admin import EventAdmin, PreferenceAdmin
from .env import SessionLocal
from datetime import datetime

class EventService:
    """Service layer for event operations"""
    
    @staticmethod
    def create_event(creator_id: int, title: str, description: str, 
                     event_type: str, start_date: datetime, end_date: datetime):
        """Create new event"""
        db = SessionLocal()
        try:
            event = EventAdmin.create_event(db, creator_id, title, description, 
                                           event_type, start_date, end_date)
            return event
        finally:
            db.close()
    
    @staticmethod
    def invite_participant(event_id: int, user_id: int):
        """Invite user to event"""
        db = SessionLocal()
        try:
            participant = Participant(event_id=event_id, user_id=user_id)
            db.add(participant)
            db.commit()
            return participant
        finally:
            db.close()
    
    @staticmethod
    def add_time_slot(event_id: int, slot_date=None, start_time=None, end_time=None):
        """Add time slot to event"""
        db = SessionLocal()
        try:
            slot = TimeSlot(
                event_id=event_id,
                slot_date=slot_date,
                start_time=start_time,
                end_time=end_time
            )
            db.add(slot)
            db.commit()
            return slot
        finally:
            db.close()
    
    @staticmethod
    def set_preference(event_id: int, user_id: int, time_slot_id: int, status: str):
        """Set or update user preference for a time slot"""
        db = SessionLocal()
        try:
            # Check if preference exists
            preference = db.query(Preference).filter(
                Preference.event_id == event_id,
                Preference.user_id == user_id,
                Preference.time_slot_id == time_slot_id
            ).first()
            
            if preference:
                preference.status = PreferenceStatus[status.upper()]
                preference.updated_at = datetime.utcnow()
            else:
                preference = Preference(
                    event_id=event_id,
                    user_id=user_id,
                    time_slot_id=time_slot_id,
                    status=PreferenceStatus[status.upper()]
                )
                db.add(preference)
            
            # Update participant response time
            participant = db.query(Participant).filter(
                Participant.event_id == event_id,
                Participant.user_id == user_id
            ).first()
            
            if participant:
                participant.responded_at = datetime.utcnow()
            
            db.commit()
            return preference
        finally:
            db.close()
    
    @staticmethod
    def get_event_details(event_id: int):
        """Get event details with all preferences"""
        db = SessionLocal()
        try:
            return EventAdmin.get_event_overview(db, event_id)
        finally:
            db.close()
    
    @staticmethod
    def finalize_event(event_id: int):
        """Finalize event, calculate best slot, and notify participants"""
        db = SessionLocal()
        try:
            # Check quorum
            quorum_status = PreferenceAdmin.check_quorum(db, event_id, quorum_percentage=0.5)
            
            # Calculate best slot
            best_slot = PreferenceAdmin.calculate_best_slot(db, event_id)
            
            # Close event
            EventAdmin.close_event(db, event_id)
            
            return {
                "quorum_status": quorum_status,
                "best_slot": best_slot,
                "event_overview": EventAdmin.get_event_overview(db, event_id)
            }
        finally:
            db.close()
# Create your views here.
