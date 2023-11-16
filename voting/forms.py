from django import forms
from .models import *
from account.forms import FormSettings


class VoterForm(FormSettings):
    class Meta:
        model = Voter
        fields = ["admission_number", "year_of_study"]


class PositionForm(FormSettings):
    class Meta:
        model = Position
        fields = ["name", "max_vote"]


class CandidateForm(FormSettings):
    class Meta:
        model = Candidate
        fields = [
            "fullname",
            "admission_number",
            "year_of_study",
            "bio",
            "position",
            "photo",
        ]


class SuggestionForm(FormSettings):
    class Meta:
        model = Suggestion
        fields = ["content"]
        widget = {
            "content": forms.Textarea(
                attrs={"placeholder": "write your proposal here ..."}
            )
        }
