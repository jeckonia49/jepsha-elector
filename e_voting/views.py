from django.views.generic import TemplateView
from django.shortcuts import redirect, render


class HeliosView(TemplateView):
    template_name = "e_voting/home.html"


class JepshaElectorPrivacyView(TemplateView):
    template_name = "e_voting/privacy.html"


class JepshaElectorAboutView(TemplateView):
    template_name = "e_voting/about.html"


class JepshaElectorFaqView(TemplateView):
    template_name = "e_voting/faq.html"


class JepshaElectorDocsView(TemplateView):
    template_name = "e_voting/docs.html"


def handler404(request, exception):
    return render(request, "e_voting/404.html")


def handler500(request, *args, **argv):
    return render(request, "e_voting/500.html")
