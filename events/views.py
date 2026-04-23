from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Event, TimeSlot, Vote
from .serializers import (
    EventSerializer,
    EventCreateSerializer,
    TimeSlotSerializer,
    VoteSerializer,
)


def health_check(request):
    return JsonResponse({"status": "ok"})


# --- EVENT VIEWS ---

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventCreateSerializer
        return EventSerializer


class EventDetailView(generics.RetrieveDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'pk'


# --- TIMESLOT VIEWS ---

class TimeSlotListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeSlotSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        return TimeSlot.objects.filter(event_id=event_id)

    def perform_create(self, serializer):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(pk=event_id)
        serializer.save(event=event)


# --- VOTE VIEWS ---

class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer