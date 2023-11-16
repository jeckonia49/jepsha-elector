from django.db import models
from account.models import CustomUser

# Create your models here.


class Voter(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # phone = models.CharField(max_length=11, unique=True)  # Used for OTP
    voted = models.BooleanField(default=False)
    admission_number = models.CharField(max_length=100, unique=True)
    year_of_study = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField()
    priority = models.IntegerField()

    def __str__(self):
        return self.name


class Candidate(models.Model):
    fullname = models.CharField(max_length=50)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    bio = models.TextField()
    photo = models.ImageField(upload_to="candidates")
    admission_number = models.CharField(max_length=100, unique=True)
    year_of_study = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.fullname


class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)


class ElectionResultPdf(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results_owner",
    )
    report = models.FileField(upload_to="results/")

    def __str__(self):
        return f"{self.report.name}".split(".")[0]


class ElectionMilbox(models.Model):
    plaintif = models.ForeignKey(
        Voter, on_delete=models.CASCADE, related_name="voter_complaint"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    complaint = models.TextField(max_length=1000)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.plaintif.admin.email}"


class ElectionMilboxReply(models.Model):
    electionmailbox = models.ForeignKey(
        ElectionMilbox, on_delete=models.CASCADE, related_name="voter_complaint_reply"
    )
    reply = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"{self.electionmailbox.pk}"


class Suggestion(models.Model):
    voter = models.ForeignKey(
        Voter, on_delete=models.CASCADE, related_name="suggestion_voter"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    implemented = models.BooleanField(default=False)

    def __str__(self):
        return f"Proposal ID: {self.pk}"
