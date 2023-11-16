from django.contrib import admin
from .models import (
    Voter,
    ElectionMilbox,
    ElectionMilboxReply,
    Suggestion,
    ElectionResultPdf,
)


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = [
        "admin",
        "voted",
        "admission_number",
        "year_of_study",
    ]
    list_filter = ["voted", "year_of_study"]


class ElectionMilboxReplyInline(admin.StackedInline):
    model = ElectionMilboxReply
    extra = 0


@admin.register(ElectionMilbox)
class ElectionMilboxAdmin(admin.ModelAdmin):
    list_display = [
        "plaintif",
        "timestamp",
        "read",
    ]
    list_filter = [
        "read",
    ]
    inlines = (ElectionMilboxReplyInline,)
    actions = (
        "_make_read",
        "_make_unread",
    )

    def _make_read(self, modelname, queryset):
        queryset.update(read=True)

    _make_read.short_description = "Mark selected items as read"

    def _make_unread(self, modelname, queryset):
        queryset.update(read=False)

    _make_unread.short_description = "Mark selected items as unread"


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ["voter", "implemented", "timestamp"]
    list_filter = ["implemented"]


@admin.register(ElectionResultPdf)
class ElectionResultPdfAdmin(admin.ModelAdmin):
    list_display = ["report", "user"]
