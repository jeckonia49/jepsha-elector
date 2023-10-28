from django.views.generic import TemplateView
from django.shortcuts import redirect, render


class HeliosView(TemplateView):
    template_name = "home.html"


class JepshaElectorPrivacyView(TemplateView):
    template_name = "privacy.html"


class JepshaElectorAboutView(TemplateView):
    template_name = "about.html"


class JepshaElectorFaqView(TemplateView):
    template_name = "faq.html"


class JepshaElectorDocsView(TemplateView):
    template_name = "docs.html"


def handler404(request, exception):
    return render(request, "404.html")


def handler500(request, *args, **argv):
    return render(request, "500.html")
