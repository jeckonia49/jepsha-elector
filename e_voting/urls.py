from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings, views

urlpatterns = [
    path("", views.HeliosView.as_view(), name="home"),
    path("about/", views.JepshaElectorAboutView.as_view(), name="about-us"),
    path("docs/", views.JepshaElectorDocsView.as_view(), name="docs"),
    path("faqs/", views.JepshaElectorFaqView.as_view(), name="faqs"),
    path("privacy/", views.JepshaElectorPrivacyView.as_view(), name="privacy"),
    path("account/", include("account.urls")),
    path("admin/", admin.site.urls),
    path("administrator/", include("administrator.urls")),
    path("voting/", include("voting.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = "e_voting.views.handler404"
handler500 = "e_voting.views.handler500"
