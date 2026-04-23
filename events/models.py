from django.db import models
import uuid

# Create your models here.
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TimeSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.event.title}: {self.start_time} - {self.end_time}"


class Vote(models.Model):
    VOTE_CHOICES = [
        ('yes', 'Yes'),
        ('maybe', 'Maybe'),
        ('no', 'No'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='votes')
    voter_name = models.CharField(max_length=100)
    choice = models.CharField(max_length=5, choices=VOTE_CHOICES, default='yes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['time_slot', 'voter_name']

    def __str__(self):
        return f"{self.voter_name} → {self.choice} for {self.time_slot}"