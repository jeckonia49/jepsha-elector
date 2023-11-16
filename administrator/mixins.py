from django.views.generic import View
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from voting.models import Position, Candidate, Voter, Votes


class DeleteMixin(View):
    queryset = None
    success_url = ""
    error_message = "Error Access This Resource"
    access_denied_message = "Access Denied. Only post request"
    success_message = ""

    def get(self, request, *args, **kwargs):
        messages.error(request, self.access_denied_message)

    def post(self, request, *args, **kwargs):
        try:
            admin = self.queryset.objects.get(id=request.POST.get("id")).admin
            admin.delete()
            admin.save()
            messages.success(request, self.success_message)
        except:
            messages.error(request, self.error_message)
        return redirect(reverse(self.success_url))


class BallotResultsMixin:
    find_winers = None

    def get_context_data(self, *args, **kwargs):
        title = "E-voting"
        try:
            file = open(settings.ELECTION_TITLE_PATH, "r")
            title = file.read()
        except:
            pass
        context = {}
        position_data = {}
        for position in Position.objects.all():
            candidate_data = []
            winner = ""
            for candidate in Candidate.objects.filter(position=position):
                this_candidate_data = {}
                votes = Votes.objects.filter(candidate=candidate).count()
                this_candidate_data["name"] = candidate.fullname
                this_candidate_data["votes"] = votes
                this_candidate_data["contestant"] = candidate
                candidate_data.append(this_candidate_data)
            print(
                "Candidate Data For  ", str(position.name), " = ", str(candidate_data)
            )
            # ! Check Winner
            if len(candidate_data) < 1:
                winner = "Position does not have candidates"
            else:
                # Check if max_vote is more than 1
                if position.max_vote > 1:
                    winner = self.find_winers(candidate_data, position.max_vote)
                else:
                    winner = max(candidate_data, key=lambda x: x["votes"])
                    if winner["votes"] == 0:
                        winner = "No one has voted for this position, yet."
                    else:
                        """
                        https://stackoverflow.com/questions/18940540/how-can-i-count-the-occurrences-of-an-item-in-a-list-of-dictionaries
                        """
                        count = sum(
                            1
                            for d in candidate_data
                            if d.get("votes") == winner["votes"]
                        )
                        if count > 1:
                            winner = f"There are {count} candidates with {winner['votes']} votes"
                        else:
                            winner = "Winner : " + winner["name"]
            print(
                "Candidate Data For  ", str(position.name), " = ", str(candidate_data)
            )
            position_data[position.name] = {
                "candidate_data": candidate_data,
                "winner": winner,
                "max_vote": position.max_vote,
            }
        context["positions"] = position_data
        return context
