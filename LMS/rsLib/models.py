from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class IssueRequest(models.Model):
    title = models.CharField(max_length=100)
    volume_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class IssuedBook(models.Model):
    title = models.CharField(max_length=100)
    volume_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
