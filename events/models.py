import uuid
from django.db import models


class Event(models.Model):
    EVENT_TYPES = [
        ('full_day', 'Full Day'),
        ('time_based', 'Time Based'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES, default='time_based')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.event_type})"


class TimeSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.event.title}: {self.start_time} - {self.end_time}"

    @property
    def available_count(self):
        return self.votes.filter(choice='available').count()

    @property
    def maybe_count(self):
        return self.votes.filter(choice='maybe').count()

    @property
    def unavailable_count(self):
        return self.votes.filter(choice='unavailable').count()

    @property
    def score(self):
        """Score for ranking: available=2, maybe=1, unavailable=0"""
        return (self.available_count * 2) + (self.maybe_count * 1)


class Vote(models.Model):
    VOTE_CHOICES = [
        ('available', 'Available'),
        ('maybe', 'Maybe'),
        ('unavailable', 'Unavailable'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='votes')
    voter_name = models.CharField(max_length=100)
    choice = models.CharField(max_length=15, choices=VOTE_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['time_slot', 'voter_name']

    def __str__(self):
        return f"{self.voter_name} → {self.choice}"