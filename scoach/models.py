import os

import django
from django.db import models
from django.core import management

from scoach.constants import constants
from scoach.utils import load_config_file_to_envs, setup_django


setup_django()


class Model(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    config = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Model #{self.id} (desc={self.description},created={self.date_created})"


class Script(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    path = models.TextField()

    def __str__(self):
        return f"Script #{self.id} (desc={self.description},created={self.date_created})"


class Parameters(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    config = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Parameters #{self.id} (desc={self.description},created={self.date_created})"


class Weights(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    path = models.TextField()

    def __str__(self):
        return f"Weights #{self.id} (desc={self.description},created={self.date_created})"


class Status(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.TextField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.status}"


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Tag {self.name} (desc={self.description})"


class Run(models.Model):
    id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    parameters = models.ForeignKey(Parameters, on_delete=models.CASCADE)
    weights = models.ForeignKey(Weights, on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    train_score = models.FloatField(blank=True, null=True)
    validation_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Run #{self.id} (status={self.status},tags={[t.name for t in self.tags.all()]},created={self.date_created})"


# class Dataset(models.Model):
#     id = models.AutoField(primary_key=True)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_modified = models.DateTimeField(auto_now=True)
#     description = models.TextField(blank=True, null=True)
#     path = models.TextField()

#     def __str__(self):
#         return f"Dataset #{self.id} (desc={self.description},path={self.path},created={self.date_created})"
