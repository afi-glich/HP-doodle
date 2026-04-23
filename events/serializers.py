from rest_framework import serializers
from .models import Event, TimeSlot, Vote


# ──────────────────────────────────────
# VOTE SERIALIZERS
# ──────────────────────────────────────

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'time_slot', 'voter_name', 'choice', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class VoteCreateUpdateSerializer(serializers.ModelSerializer):
    """Creates a new vote OR updates if voter already voted on this slot"""
    class Meta:
        model = Vote
        fields = ['id', 'time_slot', 'voter_name', 'choice']
        read_only_fields = ['id']

    def create(self, validated_data):
        # If vote already exists for this voter+slot → update it
        vote, created = Vote.objects.update_or_create(
            time_slot=validated_data['time_slot'],
            voter_name=validated_data['voter_name'],
            defaults={'choice': validated_data['choice']}
        )
        return vote


# ──────────────────────────────────────
# TIMESLOT SERIALIZERS
# ──────────────────────────────────────

class TimeSlotSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)
    available_count = serializers.IntegerField(read_only=True)
    maybe_count = serializers.IntegerField(read_only=True)
    unavailable_count = serializers.IntegerField(read_only=True)
    score = serializers.IntegerField(read_only=True)

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'event', 'start_time', 'end_time',
            'votes', 'available_count', 'maybe_count',
            'unavailable_count', 'score'
        ]
        read_only_fields = ['id']


# ──────────────────────────────────────
# EVENT SERIALIZERS
# ──────────────────────────────────────

class EventSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type',
            'created_at', 'updated_at', 'time_slots'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventCreateSerializer(serializers.ModelSerializer):
    time_slots = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'event_type', 'time_slots']
        read_only_fields = ['id']

    def create(self, validated_data):
        time_slots_data = validated_data.pop('time_slots')
        event = Event.objects.create(**validated_data)
        for slot in time_slots_data:
            TimeSlot.objects.create(
                event=event,
                start_time=slot['start_time'],
                end_time=slot['end_time']
            )
        return event


# ──────────────────────────────────────
# RESULTS SERIALIZER
# ──────────────────────────────────────

class TimeSlotResultSerializer(serializers.ModelSerializer):
    available_count = serializers.IntegerField(read_only=True)
    maybe_count = serializers.IntegerField(read_only=True)
    unavailable_count = serializers.IntegerField(read_only=True)
    score = serializers.IntegerField(read_only=True)
    voters = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'start_time', 'end_time',
            'available_count', 'maybe_count', 'unavailable_count',
            'score', 'voters'
        ]

    def get_voters(self, obj):
        return [
            {
                'voter_name': vote.voter_name,
                'choice': vote.choice
            }
            for vote in obj.votes.all()
        ]


class EventResultsSerializer(serializers.Serializer):
    """Overview of all responses + best option"""
    event = EventSerializer()
    total_participants = serializers.IntegerField()
    all_participants = serializers.ListField(child=serializers.CharField())
    time_slots_ranked = TimeSlotResultSerializer(many=True)
    best_slot = TimeSlotResultSerializer(allow_null=True)