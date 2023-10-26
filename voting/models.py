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
