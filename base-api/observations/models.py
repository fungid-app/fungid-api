from django.db import models
from taxonomy.models import Species
# Create your models here.


class Observer(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Observations(models.Model):
    date = models.DateField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    public = models.BooleanField(default=True)
    species = models.ForeignKey(
        Species, on_delete=models.DO_NOTHING, related_name="observations")
    observer = models.ForeignKey(
        Observer, on_delete=models.DO_NOTHING, related_name="observations")


class ObservationImage(models.Model):
    url = models.URLField()
    observation = models.ForeignKey(
        Observations, on_delete=models.CASCADE, related_name="images")
    isThumbnail = models.BooleanField(default=False)
