from django.shortcuts import render, reverse, redirect
from voting.models import Voter, Position, Candidate, Votes
from account.forms import CustomUserForm
from voting.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.generic import View, TemplateView
from voting.models import ElectionMilbox
from .forms import ElectionMailBoxForm, ElectionMailBoxReplyForm
from .mixins import DeleteMixin, BallotResultsMixin
from django.utils import timezone
from xhtml2pdf import pisa
from django.template.loader import get_template
from voting.models import ElectionResultPdf

# from django_renderpdf.views import PDFView


def find_n_winners(data, n):
    """Read More
    https://www.geeksforgeeks.org/python-program-to-find-n-largest-elements-from-a-list/
    """
    final_list = []
    candidate_data = data[:]
    for i in range(0, n):
        max1 = 0
        if len(candidate_data) == 0:
            continue
        this_winner = max(candidate_data, key=lambda x: x["votes"])
        # TODO: Check if None
        this = this_winner["name"] + " with " + str(this_winner["votes"]) + " votes"
        final_list.append(this)
        candidate_data.remove(this_winner)
    return ", &nbsp;".join(final_list)


class PrintView(BallotResultsMixin, TemplateView):
    template_name = "admin/print.html"
    prompt_download = True
    find_winers = find_n_winners

    @property
    def download_name(self):
        return "result.pdf"


class DownloadElectionResults(BallotResultsMixin, View):
    template_name = "admin/results.html"

    def get(self, request, *args, **kwargs):
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type="application/pdf")
        filename = f"{request.user.username}_election_report.pdf"
        response["Content-Disposition"] = f"filename={filename}"
        # find the template and render it.
        template = get_template(self.template_name)
        html = template.render(self.get_context_data(*args, **kwargs))
        # create a pdf
        pisa_status = pisa.CreatePDF(html, dest=response)

        # if error then show some funny view
        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>")
        return response

    def save_pdf_2db(self, request, report, *args, **kwargs):
        file = ElectionResultPdf.objects.filter(user=request.user, report=report)
        if file.exists():
            pass
        else:
            file = ElectionResultPdf.objects.create(user=request.user, report=report)
            file.save()

    def get_context_data(self, *args, **kwargs):
        context = super(DownloadElectionResults, self).get_context_data(*args, **kwargs)
        context["today"] = timezone.now().date()
        context["administrator"] = self.request.user
        return context


def dashboard(request):
    positions = Position.objects.all().order_by("priority")
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    voted_voters = Voter.objects.filter(voted=1)
    list_of_candidates = []
    votes_count = []
    chart_data = {}

    for position in positions:
        list_of_candidates = []
        votes_count = []
        for candidate in Candidate.objects.filter(position=position):
            list_of_candidates.append(candidate.fullname)
            votes = Votes.objects.filter(candidate=candidate).count()
            votes_count.append(votes)
        chart_data[position] = {
            "candidates": list_of_candidates,
            "votes": votes_count,
            "pos_id": position.id,
        }

    context = {
        "position_count": positions.count(),
        "candidate_count": candidates.count(),
        "voters_count": voters.count(),
        "voted_voters_count": voted_voters.count(),
        "positions": positions,
        "chart_data": chart_data,
        "page_title": "Dashboard",
    }
    return render(request, "admin/home.html", context)


def voters(request):
    voters = Voter.objects.all()
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {
        "form1": userForm,
        "form2": voterForm,
        "voters": voters,
        "page_title": "Voters List",
    }
    if request.method == "POST":
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "New voter created")
        else:
            messages.error(request, f"Form validation failed {voterForm.errors}")
    return render(request, "admin/voters.html", context)


def view_voter_by_id(request):
    voter_id = request.GET.get("id", None)
    voter = Voter.objects.filter(id=voter_id)
    context = {}
    if not voter.exists():
        context["code"] = 404
    else:
        context["code"] = 200
        voter = voter[0]
        context["first_name"] = voter.admin.first_name
        context["last_name"] = voter.admin.last_name
        context["admission_number"] = voter.admission_number
        context["year_of_study"] = voter.year_of_study
        context["id"] = voter.id
        context["email"] = voter.admin.email
    return JsonResponse(context)


def view_position_by_id(request):
    pos_id = request.GET.get("id", None)
    pos = Position.objects.filter(id=pos_id)
    context = {}
    if not pos.exists():
        context["code"] = 404
    else:
        context["code"] = 200
        pos = pos[0]
        context["name"] = pos.name
        context["max_vote"] = pos.max_vote
        context["id"] = pos.id
    return JsonResponse(context)


def updateVoter(request):
    if request.method != "POST":
        messages.error(request, "Access Denied")
    try:
        instance = Voter.objects.get(id=request.POST.get("id"))
        user = CustomUserForm(request.POST or None, instance=instance.admin)
        voter = VoterForm(request.POST or None, instance=instance)
        user.save()
        voter.save()
        messages.success(request, "Voter's bio updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse("adminViewVoters"))


class DeleteVoter(DeleteMixin):
    queryset = Voter
    success_url = "adminViewVoters"
    success_message = "Voter Successfully Deleted"


def viewPositions(request):
    positions = Position.objects.order_by("-priority").all()
    form = PositionForm(request.POST or None)
    context = {"positions": positions, "form1": form, "page_title": "Positions"}
    if request.method == "POST":
        if form.is_valid():
            form = form.save(commit=False)
            form.priority = positions.count() + 1  # Just in case it is empty.
            form.save()
            messages.success(request, "New Position Created")
        else:
            messages.error(request, "Form errors")
    return render(request, "admin/positions.html", context)


def updatePosition(request):
    if request.method != "POST":
        messages.error(request, "Access Denied")
    try:
        instance = Position.objects.get(id=request.POST.get("id"))
        pos = PositionForm(request.POST or None, instance=instance)
        pos.save()
        messages.success(request, "Position has been updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse("viewPositions"))


class DeletePosition(DeleteMixin):
    queryset = Position
    success_url = "viewPositions"
    success_message = "Position Deleted Successfully"

    def post(self, request, *args, **kwargs):
        try:
            position = self.queryset.objects.get(id=request.POST.get("id"))
            position.delete()
            messages.success(request, self.success_message)
            return redirect(reverse(self.success_url))
        except:
            messages.error(request, self.error_message)
            return redirect(reverse(self.success_url))


def viewCandidates(request):
    candidates = Candidate.objects.all()
    form = CandidateForm(request.POST or None, request.FILES or None)
    context = {"candidates": candidates, "form1": form, "page_title": "Candidates"}
    if request.method == "POST":
        if form.is_valid():
            form = form.save()
            messages.success(request, "New Candidate Created")
        else:
            messages.error(request, "Form errors")
    return render(request, "admin/candidates.html", context)


def updateCandidate(request):
    if request.method != "POST":
        messages.error(request, "Access Denied")
    try:
        candidate_id = request.POST.get("id")
        candidate = Candidate.objects.get(id=candidate_id)
        form = CandidateForm(
            request.POST or None, request.FILES or None, instance=candidate
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate Data Updated")
        else:
            messages.error(request, "Form has errors")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse("viewCandidates"))


class DeleteCandidate(DeleteMixin):
    queryset = Candidate
    success_url = "viewCandidates"
    success_message = "Candidate Deleted Successfully"

    def post(self, request, *args, **kwargs):
        try:
            candidate = self.queryset.objects.get(id=request.POST.get("id"))
            candidate.delete()
            messages.success(request, self.success_message)
            return redirect(reverse(self.success_url))
        except:
            messages.error(request, self.error_message)
            return redirect(reverse(self.success_url))


def view_candidate_by_id(request):
    candidate_id = request.GET.get("id", None)
    candidate = Candidate.objects.filter(id=candidate_id)
    context = {}
    if not candidate.exists():
        context["code"] = 404
    else:
        candidate = candidate[0]
        context["code"] = 200
        context["fullname"] = candidate.fullname
        previous = CandidateForm(instance=candidate)
        context["form"] = str(previous.as_p())
    return JsonResponse(context)


class BallotPositionView(TemplateView):
    template_name = "admin/ballot_position.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Ballot Position"
        return context


def update_ballot_position(request, position_id, up_or_down):
    try:
        context = {"error": False}
        position = Position.objects.get(id=position_id)
        if up_or_down == "up":
            priority = position.priority - 1
            if priority == 0:
                context["error"] = True
                output = "This position is already at the top"
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority + 1)
                )
                position.priority = priority
                position.save()
                output = "Moved Up"
        else:
            priority = position.priority + 1
            if priority > Position.objects.all().count():
                output = "This position is already at the bottom"
                context["error"] = True
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority - 1)
                )
                position.priority = priority
                position.save()
                output = "Moved Down"
        context["message"] = output
    except Exception as e:
        context["message"] = e

    return JsonResponse(context)


def ballot_title(request):
    from urllib.parse import urlparse

    url = urlparse(request.META["HTTP_REFERER"]).path
    from django.urls import resolve

    try:
        redirect_url = resolve(url)
        title = request.POST.get("title", "No Name")
        file = open(settings.ELECTION_TITLE_PATH, "w")
        file.write(title)
        file.close()
        messages.success(request, "Election title has been changed to " + str(title))
        return redirect(url)
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


class VotesListView(TemplateView):
    template_name = "admin/votes.html"
    votes = Votes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["votes"] = self.votes.objects.all()
        context["page_title"] = "Votes"
        return context


def view_vote_by_id(request):
    vote_id = request.GET.get("id")
    vote = Votes.objects.filter(id=vote_id)
    context = {}
    if not vote.exists():
        context["code"] = 404
    else:
        vote = vote[0]
        context[
            "fullname"
        ] = f"{vote.voter.admin.last_name} {vote.voter.admin.first_name}"
    return JsonResponse(context)


class DeleteVote(DeleteMixin):
    queryset = Votes
    success_url = "viewVotes"
    success_message = "Vote Deleted Successfully"

    def post(self, request, *args, **kwargs):
        try:
            vote = self.queryset.objects.get(id=request.POST.get("id"))
            vote.delete()
            messages.success(request, self.success_message)
            return redirect(reverse(self.success_url))
        except:
            messages.error(request, self.error_message)
            return redirect(reverse(self.success_url))


class ResetVotesView(TemplateView):
    def get(self, request, *args, **kwargs):
        Votes.objects.all().delete()
        Voter.objects.all().update(voted=False)
        messages.success(request, "All votes has been reset")
        return redirect(reverse("viewVotes"))


class ElectionMilboxView(TemplateView):
    template_name = "mailbox/inbox.html"
    queryset = ElectionMilbox
    form_class = ElectionMailBoxReplyForm

    def get_queryset(self):
        return self.queryset.objects.filter(read=False).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Inbox"
        context["mailbox"] = self.get_queryset()
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            mail_id = request.POST.get("mail_id")
            mail = self.queryset.objects.get(pk=int(mail_id))
            instance = form.save(commit=False)
            instance.electionmailbox = mail
            mail.read = True
            mail.save()
            instance.save()
            form.save()
            messages.success(
                request,
                f"You're response was sent succesfully to {instance.electionmailbox.plaintif}",
            )
        return redirect(reverse("viewMessages"))


class MarkMailboxReadView(View):
    queryset = ElectionMilbox

    def get_queryset(self):
        return self.queryset.objects.filter(read=False).all()

    def post(self, request, *args, **kwargs):
        self.get_queryset().delete()
        messages.success(request, "All Messages Marked as Read")
        return redirect(reverse("viewMessages"))
