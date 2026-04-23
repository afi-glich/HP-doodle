from rest_framework import serializers
from .models import Event, TimeSlot, Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'time_slot', 'voter_name', 'choice', 'created_at']
        read_only_fields = ['id', 'created_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)

    class Meta:
        model = TimeSlot
        fields = ['id', 'event', 'start_time', 'end_time', 'votes']
        read_only_fields = ['id']


class EventSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'time_slots']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventCreateSerializer(serializers.ModelSerializer):
    time_slots = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'time_slots']
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