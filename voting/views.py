from django.shortcuts import render, redirect, reverse, get_object_or_404
from account.views import account_login
from .models import Position, Candidate, Voter, Votes
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
import requests
import json
from django.contrib.auth import get_user
from administrator.forms import ElectionMailBoxForm
from django.views.generic import TemplateView, View
from .forms import SuggestionForm, VoterForm

# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}
    # return render(request, "voting/login.html", context)


def generate_ballot(display_controls=False):
    positions = Position.objects.order_by("priority").all()
    output = ""
    candidates_data = ""
    num = 1
    # return None
    for position in positions:
        name = position.name
        position_name = slugify(name)
        candidates = Candidate.objects.filter(position=position)
        for candidate in candidates:
            if position.max_vote > 1:
                instruction = (
                    "You may select up to " + str(position.max_vote) + " candidates"
                )
                input_box = (
                    '<input type="checkbox" value="'
                    + str(candidate.id)
                    + '" class="flat-red '
                    + position_name
                    + '" name="'
                    + position_name
                    + "[]"
                    + '">'
                )
            else:
                instruction = "Select only one candidate"
                input_box = (
                    '<input value="'
                    + str(candidate.id)
                    + '" type="radio" class="flat-red '
                    + position_name
                    + '" name="'
                    + position_name
                    + '">'
                )
            candidates_data = (
                candidates_data
                + "<li>"
                + input_box
                + '<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="'
                + candidate.fullname
                + '" data-bio="'
                + candidate.bio
                + '"><i class="fa fa-search"></i> Manifesto</button><span class="cname clist">'
                + candidate.fullname
                + '<span class="cname clist">'
                + str(candidate.admission_number)
            )
        up = ""
        if position.priority == 1:
            up = "disabled"
        down = ""
        if position.priority == positions.count():
            down = "disabled"
        output = (
            output
            + f"""<div class="row">	<div class="col-xs-12"><div class="box box-solid" id="{position.id}">
             <div class="box-header with-border">
            <h3 class="box-title"><b>{name}</b></h3>"""
        )

        if display_controls:
            output = (
                output
                + f""" <div class="pull-right box-tools">
        <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> </button>
        <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
        </div>"""
            )

        output = (
            output
            + f"""</div>
        <div class="box-body">
        <p>
        <span class="pull-right">
        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
        </span>
        </p>
        <div id="candidate_list">
        <ul>
        {candidates_data}
        </ul>
        </div>
        </div>
        </div>
        </div>
        </div>
        """
        )
        position.priority = num
        position.save()
        num = num + 1
        candidates_data = ""
    return output


def fetch_ballot(request):
    output = generate_ballot(display_controls=True)
    return JsonResponse(output, safe=False)


# def generate_otp():
#     """Link to this function
#     https://www.codespeedy.com/otp-generation-using-random-module-in-python/
#     """
#     import random as r

#     otp = ""
#     for i in range(r.randint(5, 8)):
#         otp += str(r.randint(1, 9))
#     return otp


def dashboard(request):
    user = request.user
    # * Check if this voter has been verified
    # if user.voter.otp is None or user.voter.verified == False:
    #     if not settings.SEND_OTP:
    #         # Bypass
    #         msg = bypass_otp()
    #         messages.success(request, msg)
    #         return redirect(reverse('show_ballot'))
    #     else:
    #         return redirect(reverse('voterVerify'))
    # else:
    if user.voter.voted:  # * User has voted
        # To display election result or candidates I voted for ?
        context = {
            "my_votes": Votes.objects.filter(voter=user.voter),
        }
        return render(request, "voting/voter/result.html", context)
    else:
        return redirect(reverse("show_ballot"))


class ElectionMailBoxView(TemplateView):
    template_name = "voting/voter/report.html"
    form_class = ElectionMailBoxForm
    voter = Voter

    def get_custom_user(self):
        return get_user(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Complaint/Reporting"
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.plaintif = Voter.objects.get(admin=self.get_custom_user())
            instance.save()
            form.save()
            messages.success(
                request, f"Your message was successfully submitted. Thanks!"
            )
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        messages.success(
            request,
            f"An error occurred will submitting your message. Please try again.",
        )
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class ProposalSuggestionView(TemplateView):
    template_name = "voting/voter/proposal.html"
    form_class = SuggestionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.voter = Voter.objects.get(admin=request.user)
            instance.save()
            form.save()
            messages.success(request, "Your proposal was sent successfully.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        messages.error(request, "Error sending your message. Tyr again.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def show_ballot(request):
    if request.user.voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse("voterDashboard"))
    ballot = generate_ballot(display_controls=False)
    context = {"ballot": ballot}
    return render(request, "voting/voter/ballot.html", context)


def preview_vote(request):
    if request.method != "POST":
        error = True
        response = "Please browse the system properly"
    else:
        output = ""
        form = dict(request.POST)
        # We don't need to loop over CSRF token
        form.pop("csrfmiddlewaretoken", None)
        error = False
        data = []
        positions = Position.objects.all()
        for position in positions:
            max_vote = position.max_vote
            pos = slugify(position.name)
            pos_id = position.id
            if position.max_vote > 1:
                this_key = pos + "[]"
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                if len(form_position) > max_vote:
                    error = True
                    response = (
                        "You can only choose "
                        + str(max_vote)
                        + " candidates for "
                        + position.name
                    )
                else:
                    # for key, value in form.items():
                    start_tag = f"""
                       <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'>
                                <ul style='list-style-type:none; margin-left:-40px'>
                                
                    
                    """
                    end_tag = "</ul></span></div><hr/>"
                    data = ""
                    for form_candidate_id in form_position:
                        try:
                            candidate = Candidate.objects.get(
                                id=form_candidate_id, position=position
                            )
                            data += f"""
		                      	<li><i class="fa fa-check-square-o"></i> {candidate.fullname}</li>
                            """
                        except:
                            error = True
                            response = "Please, browse the system properly"
                    output += start_tag + data + end_tag
            else:
                this_key = pos
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                # Max Vote == 1
                try:
                    form_position = form_position[0]
                    candidate = Candidate.objects.get(
                        position=position, id=form_position
                    )
                    output += f"""
                            <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'><i class="fa fa-check-circle-o"></i> {candidate.fullname}</span>
		                    </div>
                      <hr/>
                    """
                except Exception as e:
                    error = True
                    response = "Please, browse the system properly"
    context = {"error": error, "list": output}
    return JsonResponse(context, safe=False)


def submit_ballot(request):
    if request.method != "POST":
        messages.error(request, "Please, browse the system properly")
        return redirect(reverse("show_ballot"))

    # Verify if the voter has voted or not
    voter = request.user.voter
    if voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse("voterDashboard"))

    form = dict(request.POST)
    form.pop("csrfmiddlewaretoken", None)  # Pop CSRF Token
    form.pop("submit_vote", None)  # Pop Submit Button

    # Ensure at least one vote is selected
    if len(form.keys()) < 1:
        messages.error(request, "Please select at least one candidate")
        return redirect(reverse("show_ballot"))
    positions = Position.objects.all()
    form_count = 0
    for position in positions:
        max_vote = position.max_vote
        pos = slugify(position.name)
        pos_id = position.id
        if position.max_vote > 1:
            this_key = pos + "[]"
            form_position = form.get(this_key)
            if form_position is None:
                continue
            if len(form_position) > max_vote:
                messages.error(
                    request,
                    "You can only choose "
                    + str(max_vote)
                    + " candidates for "
                    + position.name,
                )
                return redirect(reverse("show_ballot"))
            else:
                for form_candidate_id in form_position:
                    form_count += 1
                    try:
                        candidate = Candidate.objects.get(
                            id=form_candidate_id, position=position
                        )
                        vote = Votes()
                        vote.candidate = candidate
                        vote.voter = voter
                        vote.position = position
                        vote.save()
                    except Exception as e:
                        messages.error(
                            request, "Please, browse the system properly " + str(e)
                        )
                        return redirect(reverse("show_ballot"))
        else:
            this_key = pos
            form_position = form.get(this_key)
            if form_position is None:
                continue
            # Max Vote == 1
            form_count += 1
            try:
                form_position = form_position[0]
                candidate = Candidate.objects.get(position=position, id=form_position)
                vote = Votes()
                vote.candidate = candidate
                vote.voter = voter
                vote.position = position
                vote.save()
            except Exception as e:
                messages.error(request, "Please, browse the system properly " + str(e))
                return redirect(reverse("show_ballot"))
    # Count total number of records inserted
    # Check it viz-a-viz form_count
    inserted_votes = Votes.objects.filter(voter=voter)
    if inserted_votes.count() != form_count:
        # Delete
        inserted_votes.delete()
        messages.error(request, "An error occured. Kindly retry")
        return redirect(reverse("show_ballot"))
    else:
        # Update Voter profile to voted
        voter.voted = True
        voter.save()
        messages.success(request, "Thanks for voting")
        return redirect(reverse("voterDashboard"))


class UpdateVoterView(TemplateView):
    template_name = "voting/voter/updateVoter.html"
    form_class = VoterForm
    queryset = Voter

    def get_voter(self):
        return get_object_or_404(Voter, admin=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(
            instance=self.get_voter(),
            initial={
                "first_name": self.get_voter().admin.first_name,
                "last_name": self.get_voter().admin.last_name,
                "email": self.get_voter().admin.email,
            },
        )
        context["voter"] = self.get_voter()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request.POST,
            instance=self.get_voter(),
            initial={
                "first_name": self.get_voter().admin.first_name,
                "last_name": self.get_voter().admin.last_name,
                "email": self.get_voter().admin.email,
            },
        )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.admin.first_name = form.cleaned_data.get("first_name")
            instance.admin.last_name = form.cleaned_data.get("last_name")
            try:
                instance.admin.email = form.cleaned_data.get("email")
                instance.admin.save()
                instance.save()
                form.save()
                messages.success(request, "Your credentials were updated successfully")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            except:
                messages.error(
                    request,
                    "The email or admission number your updating to is already saved. Kindly check and retry",
                )
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
