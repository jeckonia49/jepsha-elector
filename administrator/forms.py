from voting.forms import FormSettings
from django import forms
from voting.models import ElectionMilbox, ElectionMilboxReply


class ElectionMailBoxForm(FormSettings):
    class Meta:
        model = ElectionMilbox
        fields = ["complaint"]
        widgets = {"complaint": forms.Textarea(attrs={"rows": 5, "placeholder": "Writer your complaint/reporting here ..."})}


class ElectionMailBoxReplyForm(FormSettings):
    class Meta:
        model = ElectionMilboxReply
        fields = ["reply"]
        widgets = {
            "reply": forms.Textarea(
                attrs={"placeholder": "writer your reply message here", }
            )
        }
