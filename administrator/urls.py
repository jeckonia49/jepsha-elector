from django.urls import path
from . import views


urlpatterns = [
    path("", views.dashboard, name="adminDashboard"),
    # * Voters
    path("voters/", views.voters, name="adminViewVoters"),
    path("voters/view/", views.view_voter_by_id, name="viewVoter"),
    path("voters/delete/", views.DeleteVoter.as_view(), name="deleteVoter"),
    # path("voters/delete", views.deleteVoter, name="deleteVoter"),
    # path("voters/update", views.updateVoter, name="updateVoter"),
    # # * Position
    path("position/view/", views.view_position_by_id, name="viewPosition"),
    path("position/update/", views.updatePosition, name="updatePosition"),
    path("position/delete/", views.DeletePosition.as_view(), name="deletePosition"),
    path("positions/view/", views.viewPositions, name="viewPositions"),
    # # * Candidate
    path("candidate/", views.viewCandidates, name="viewCandidates"),
    path("candidate/update/", views.updateCandidate, name="updateCandidate"),
    path("candidate/delete/", views.DeleteCandidate.as_view(), name="deleteCandidate"),
    path("candidate/view/", views.view_candidate_by_id, name="viewCandidate"),
    # # * Settings (Ballot Position and Election Title)
    path(
        "settings/ballot/position/",
        views.BallotPositionView.as_view(),
        name="ballot_position",
    ),
    path("settings/ballot/title/", views.ballot_title, name="ballot_title"),
    path(
        "settings/ballot/position/update/<int:position_id>/<str:up_or_down>/",
        views.update_ballot_position,
        name="update_ballot_position",
    ),
    # # * Votes
    path("votes/", views.VotesListView.as_view(), name="viewVotes"),
    path("votes/view/", views.view_vote_by_id, name="viewVote"),
    path("votes/reset/", views.ResetVotesView.as_view(), name="resetVote"),
    path("votes/results/", views.PrintView.as_view(), name="printResult"),
    path("votes/results/view/", views.DownloadElectionResults.as_view(), name="result"),
    path("votes/delete/", views.DeleteVote.as_view(), name="deleteVote"),
    # # * Messages
    path("mailbox/", views.ElectionMilboxView.as_view(), name="viewMessages"),
    path(
        "mailbox/read/complete/",
        views.MarkMailboxReadView.as_view(),
        name="readMessages",
    ),
]
