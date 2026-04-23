from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path("health/", views.health_check, name="health_check"),

    # Events
    path("", views.EventListCreateView.as_view(), name="event_list_create"),
    path("<uuid:pk>/", views.EventDetailView.as_view(), name="event_detail"),

    # Time Slots
    path("<uuid:event_id>/slots/", views.TimeSlotListCreateView.as_view(), name="timeslot_list_create"),
    path("slots/<uuid:pk>/", views.TimeSlotDeleteView.as_view(), name="timeslot_delete"),

    # Votes
    path("votes/", views.VoteCreateUpdateView.as_view(), name="vote_create"),
    path("votes/bulk/", views.BulkVoteView.as_view(), name="vote_bulk"),
    path("votes/<uuid:pk>/", views.VoteDeleteView.as_view(), name="vote_delete"),

    # Results
    path("<uuid:event_id>/results/", views.EventResultsView.as_view(), name="event_results"),

    # Participant votes (for updating)
    path("<uuid:event_id>/participant/<str:voter_name>/",
         views.ParticipantVotesView.as_view(), name="participant_votes"),
]