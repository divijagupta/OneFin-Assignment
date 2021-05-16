from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models


def generate_uuid():
    return str(uuid4())


class Movies(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.title


class Collection(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=generate_uuid)
    title = models.CharField(max_length=20)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection_user')
    movies = models.ManyToManyField(Movies, related_name='collection_movies')

    def __str__(self):
        return self.title


class RequestCounter(models.Model):
    counter = models.PositiveIntegerField()
