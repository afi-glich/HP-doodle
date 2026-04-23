from django.contrib import admin

from sqlalchemy.orm import Session
from .models import User, Event, TimeSlot, Preference, PreferenceStatus
from .env import SessionLocal
from datetime import datetime, timedelta

class EventAdmin:
    """Admin operations for events"""
    
    @staticmethod
    def create_event(session: Session, creator_id: int, title: str, description: str, 
                     event_type: str, start_date: datetime, end_date: datetime):
        """Create a new event"""
        from .models import Event, EventType
        
        event = Event(
            title=title,
            description=description,
            creator_id=creator_id,
            event_type=EventType[event_type.upper()],
            start_date=start_date,
            end_date=end_date
        )
        session.add(event)
        session.commit()
        return event
    
    @staticmethod
    def close_event(session: Session, event_id: int):
        """Close event and finalize best slot"""
        event = session.query(Event).filter(Event.id == event_id).first()
        if event:
            event.is_closed = True
            session.commit()
        return event
    
    @staticmethod
    def get_event_overview(session: Session, event_id: int):
        """Get comprehensive event overview"""
        event = session.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            return None
        
        overview = {
            "event": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "type": event.event_type.value,
                "creator": event.creator.username,
                "is_closed": event.is_closed,
            },
            "time_slots": [],
            "participants": [],
            "best_slot": None
        }
        
        # Add time slots with preference counts
        for slot in event.time_slots:
            slot_info = {
                "id": slot.id,
                "date": str(slot.slot_date),
                "time_range": f"{slot.start_time}-{slot.end_time}" if slot.start_time else "Full day",
                "preferences": {
                    "available": 0,
                    "unavailable": 0,
                    "maybe": 0
                },
                "total_votes": len(slot.preferences)
            }
            
            for pref in slot.preferences:
                slot_info["preferences"][pref.status.value] += 1
            
            overview["time_slots"].append(slot_info)
        
        # Add participants
        for participant in event.participants:
            overview["participants"].append({
                "id": participant.user_id,
                "username": participant.user.username,
                "responded": participant.responded_at is not None,
                "responded_at": str(participant.responded_at) if participant.responded_at else None
            })
        
        # Add best slot if determined
        if event.best_slot:
            overview["best_slot"] = {
                "id": event.best_slot.id,
                "date": str(event.best_slot.slot_date),
                "time_range": f"{event.best_slot.start_time}-{event.best_slot.end_time}" 
                              if event.best_slot.start_time else "Full day"
            }
        
        return overview

class PreferenceAdmin:
    """Admin operations for preferences"""
    
    @staticmethod
    def calculate_best_slot(session: Session, event_id: int):
        """Calculate and set the best available slot based on preferences"""
        event = session.query(Event).filter(Event.id == event_id).first()
        
        if not event or not event.time_slots:
            return None
        
        best_slot = None
        best_score = -1
        
        for slot in event.time_slots:
            score = sum(1 for p in slot.preferences if p.status == PreferenceStatus.AVAILABLE)
            
            if score > best_score:
                best_score = score
                best_slot = slot
        
        if best_slot:
            event.best_slot_id = best_slot.id
            session.commit()
        
        return best_slot
    
    @staticmethod
    def check_quorum(session: Session, event_id: int, quorum_percentage: float = 0.5):
        """Check if quorum has been reached"""
        event = session.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            return False
        
        total_participants = len(event.participants)
        responded_participants = sum(1 for p in event.participants if p.responded_at)
        
        if total_participants == 0:
            return False
        
        response_rate = responded_participants / total_participants
        
        return {
            "quorum_reached": response_rate >= quorum_percentage,
            "response_rate": response_rate,
            "responded": responded_participants,
            "total": total_participants,
            "required": int(total_participants * quorum_percentage)
        }

# Command-line interface
if __name__ == "__main__":
    db = SessionLocal()
    print("Admin interface loaded")
# Register your models here.
