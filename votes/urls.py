from django.urls import path

from .views import VoteMenuAPIView, VoteResultsForCurrentDayAPIView

urlpatterns = [
    path("vote-menu/", VoteMenuAPIView.as_view(), name="vote-menu"),
    path(
        "voting-results-for-today",
        VoteResultsForCurrentDayAPIView.as_view(),
        name="winning-menu",
    ),
]
