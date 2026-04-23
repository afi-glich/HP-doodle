from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path("health/", views.health_check, name="health_check"),

    # Events
    path("", views.EventListCreateView.as_view(), name="event_list_create"),
    path("<uuid:pk>/", views.EventDetailView.as_view(), name="event_detail"),

    # TimeSlots
    path("<uuid:event_id>/slots/", views.TimeSlotListCreateView.as_view(), name="timeslot_list_create"),

    # Votes
    path("votes/", views.VoteCreateView.as_view(), name="vote_create"),
]