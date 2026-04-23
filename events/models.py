from django.db import models
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class EventType(enum.Enum):
    FULL_DAY = "full_day"
    TIME_BASED = "time_based"

class PreferenceStatus(enum.Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MAYBE = "maybe"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    created_events = relationship("Event", back_populates="creator", foreign_keys="Event.creator_id")
    participations = relationship("Participant", back_populates="user")
    preferences = relationship("Preference", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_closed = Column(Boolean, default=False)
    best_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_events", foreign_keys=[creator_id])
    participants = relationship("Participant", back_populates="event", cascade="all, delete-orphan")
    time_slots = relationship("TimeSlot", back_populates="event", cascade="all, delete-orphan")
    preferences = relationship("Preference", back_populates="event", cascade="all, delete-orphan")
    best_slot = relationship("TimeSlot", foreign_keys=[best_slot_id], post_update=True)
    
    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, type={self.event_type.value})>"

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    slot_date = Column(Date, nullable=False)  # For full-day events
    start_time = Column(Time, nullable=True)  # For time-based events
    end_time = Column(Time, nullable=True)    # For time-based events
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="time_slots", foreign_keys=[event_id])
    preferences = relationship("Preference", back_populates="time_slot", cascade="all, delete-orphan")
    
    def __repr__(self):
        if self.start_time and self.end_time:
            return f"<TimeSlot(id={self.id}, date={self.slot_date}, time={self.start_time}-{self.end_time})>"
        return f"<TimeSlot(id={self.id}, date={self.slot_date})>"

class Participant(Base):
    __tablename__ = "participants"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invited_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    event = relationship("Event", back_populates="participants", foreign_keys=[event_id])
    user = relationship("User", back_populates="participations", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<Participant(user_id={self.user_id}, event_id={self.event_id})>"

class Preference(Base):
    __tablename__ = "preferences"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
    status = Column(Enum(PreferenceStatus), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="preferences", foreign_keys=[event_id])
    user = relationship("User", back_populates="preferences", foreign_keys=[user_id])
    time_slot = relationship("TimeSlot", back_populates="preferences", foreign_keys=[time_slot_id])
    
    def __repr__(self):
        return f"<Preference(user_id={self.user_id}, slot_id={self.time_slot_id}, status={self.status.value})>"
    