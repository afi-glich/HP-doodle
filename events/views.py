from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Event, TimeSlot, Vote
from .serializers import (
    EventSerializer,
    EventCreateSerializer,
    TimeSlotSerializer,
    VoteSerializer,
    VoteCreateUpdateSerializer,
    EventResultsSerializer,
    TimeSlotResultSerializer,
)


def health_check(request):
    return JsonResponse({"status": "ok"})


# ──────────────────────────────────────
# EVENT VIEWS
# ──────────────────────────────────────

class EventListCreateView(generics.ListCreateAPIView):
    """
    GET  → Lista tutti gli eventi
    POST → Crea evento con time slots
    """
    queryset = Event.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventCreateSerializer
        return EventSerializer


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → Dettaglio evento
    PUT    → Aggiorna evento
    DELETE → Elimina evento
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'pk'


# ──────────────────────────────────────
# TIMESLOT VIEWS
# ──────────────────────────────────────

class TimeSlotListCreateView(generics.ListCreateAPIView):
    """
    GET  → Lista time slots di un evento
    POST → Aggiungi time slot a un evento
    """
    serializer_class = TimeSlotSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        return TimeSlot.objects.filter(event_id=event_id)

    def perform_create(self, serializer):
        event_id = self.kwargs['event_id']
        event = Event.objects.get(pk=event_id)
        serializer.save(event=event)


class TimeSlotDeleteView(generics.DestroyAPIView):
    """DELETE → Elimina un time slot"""
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    lookup_field = 'pk'


# ──────────────────────────────────────
# VOTE VIEWS
# ──────────────────────────────────────

class VoteCreateUpdateView(generics.CreateAPIView):
    """
    POST → Crea voto (o aggiorna se esiste già)
    
    Voter can vote on a time slot. If they already voted,
    their vote gets UPDATED automatically.
    """
    queryset = Vote.objects.all()
    serializer_class = VoteCreateUpdateSerializer


class VoteDeleteView(generics.DestroyAPIView):
    """DELETE → Rimuovi un voto"""
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    lookup_field = 'pk'


class BulkVoteView(APIView):
    """
    POST → Vota su più time slots in una sola richiesta
    
    Body:
    {
        "voter_name": "Mario",
        "votes": [
            {"time_slot": "uuid-1", "choice": "available"},
            {"time_slot": "uuid-2", "choice": "maybe"},
            {"time_slot": "uuid-3", "choice": "unavailable"}
        ]
    }
    """
    def post(self, request):
        voter_name = request.data.get('voter_name')
        votes_data = request.data.get('votes', [])

        if not voter_name:
            return Response(
                {"error": "voter_name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        for vote_data in votes_data:
            vote, created = Vote.objects.update_or_create(
                time_slot_id=vote_data['time_slot'],
                voter_name=voter_name,
                defaults={'choice': vote_data['choice']}
            )
            results.append({
                'id': str(vote.id),
                'time_slot': str(vote.time_slot_id),
                'voter_name': vote.voter_name,
                'choice': vote.choice,
                'created': created
            })

        return Response(results, status=status.HTTP_200_OK)


# ──────────────────────────────────────
# RESULTS VIEW
# ──────────────────────────────────────

class EventResultsView(APIView):
    """
    GET → Overview di tutte le risposte + best option
    
    Returns:
    - event details
    - total participants
    - list of all participants
    - time slots ranked by score
    - best time slot (highest score)
    """
    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        time_slots = event.time_slots.all()

        # Get all unique participants
        all_participants = list(
            Vote.objects.filter(time_slot__event=event)
            .values_list('voter_name', flat=True)
            .distinct()
        )

        # Rank time slots by score (available*2 + maybe*1)
        ranked_slots = sorted(time_slots, key=lambda s: s.score, reverse=True)

        # Best slot = highest score (None if no votes)
        best_slot = ranked_slots[0] if ranked_slots and ranked_slots[0].score > 0 else None

        # Build response
        data = {
            'event': EventSerializer(event).data,
            'total_participants': len(all_participants),
            'all_participants': all_participants,
            'time_slots_ranked': TimeSlotResultSerializer(ranked_slots, many=True).data,
            'best_slot': TimeSlotResultSerializer(best_slot).data if best_slot else None,
        }

        return Response(data)


# ──────────────────────────────────────
# PARTICIPANT VIEW (what a voter voted)
# ──────────────────────────────────────

class ParticipantVotesView(APIView):
    """
    GET → Mostra tutti i voti di un partecipante per un evento
    
    Utile per pre-popolare il form quando un partecipante
    vuole AGGIORNARE le sue risposte
    """
    def get(self, request, event_id, voter_name):
        votes = Vote.objects.filter(
            time_slot__event_id=event_id,
            voter_name=voter_name
        )

        data = [
            {
                'time_slot': str(vote.time_slot_id),
                'choice': vote.choice,
                'updated_at': vote.updated_at
            }
            for vote in votes
        ]

        return Response({
            'voter_name': voter_name,
            'event_id': str(event_id),
            'votes': data
        })