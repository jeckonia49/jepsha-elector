from django.urls import path
from . import views

urlpatterns = [
    # path("", views.index),
    path("ballot/fetch/", views.fetch_ballot, name="fetch_ballot"),
    path("dashboard/", views.dashboard, name="voterDashboard"),
    path("dashboard/update", views.UpdateVoterView.as_view(), name="voterUpdate"),
    # path('verify/', views.verify, name='voterVerify'),
    path("complaint/", views.ElectionMailBoxView.as_view(), name="complaint"),
    path("proposal/", views.ProposalSuggestionView.as_view(), name="proposal"),
    # path('verify/otp', views.verify_otp, name='verify_otp'),
    # path('otp/resend/', views.resend_otp, name='resend_otp'),
    path("ballot/vote", views.show_ballot, name="show_ballot"),
    path("ballot/vote/preview", views.preview_vote, name="preview_vote"),
    path("ballot/vote/submit", views.submit_ballot, name="submit_ballot"),
]
