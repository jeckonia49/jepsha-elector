from django.shortcuts import render, redirect, reverse
from .email_backend import EmailBackend
from django.contrib import messages
from .forms import CustomUserForm
from voting.forms import VoterForm
from django.contrib.auth import login, logout
from django.views.generic import TemplateView, View
from .models import CustomUser

# Create your views here.


def account_login(request):
    if request.user.is_authenticated:
        if request.user.user_type == "1":
            return redirect(reverse("adminDashboard"))
        else:
            return redirect(reverse("voterDashboard"))

    context = {}
    if request.method == "POST":
        user = EmailBackend.authenticate(
            request,
            username=request.POST.get("email"),
            password=request.POST.get("password"),
        )
        if user != None:
            login(request, user)
            if user.user_type == "1":
                return redirect(reverse("adminDashboard"))
            else:
                return redirect(reverse("voterDashboard"))
        else:
            messages.error(request, "Invalid details")
            return redirect("account_login")

    return render(request, "voting/login.html", context)


def account_register(request):
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    context = {"form1": userForm, "form2": voterForm}
    if request.method == "POST":
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "Account created. You can login now!")
            return redirect(reverse("account_login"))
        else:
            messages.error(request, "Provided data failed validation")
            # return account_login(request)
    return render(request, "voting/reg.html", context)


def account_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        messages.success(request, "Thank you for visiting our website!")
    else:
        messages.error(request, "You need to be logged in to perform this action")

    return redirect(reverse("account_login"))


def reset_password_view(request):
    pass


class ResetPasswordView(TemplateView):
    template_name = "voting/resetpassword.html"
    custom_user = CustomUser

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home"))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_email = request.POST.get("email")
        user_password = request.POST.get("password")
        user = self.custom_user.objects.filter(email=user_email).first()
        if user:
            if len(user_password) > 8:
                user.set_password(user_password)
                user.save()
                messages.success(request, f"Your new password is {user_password}")
                return redirect(reverse("passwordresetview"))
            messages.error(request, "Password Can't be less than 8 characters")
            return redirect(reverse("passwordreset"))
        messages.error(
            request,
            f"We could not find your email in our database. Kinldy recheck and try again!",
        )
        return redirect(reverse("passwordreset"))


class ResetPasswordViewDone(TemplateView):
    template_name = "voting/resetpasswordone.html"
