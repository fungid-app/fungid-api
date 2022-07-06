from django.db import models
from taxonomy.models import Species
from django.db.models.functions import Lower


class GbifObserver(models.Model):
    constraints = [
        models.UniqueConstraint(
            Lower('name'), name='taxonomy_species_unique_name')
    ]
    name = models.CharField(max_length=255, unique=True)


class GbifObservations(models.Model):
    gbifid = models.BigIntegerField(primary_key=True)
    datecreated = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    public = models.BooleanField(default=True)
    acces_rights = models.CharField(max_length=255, null=True)
    rights_holder = models.CharField(max_length=255)
    recorded_by = models.CharField(max_length=255)
    license = models.CharField(max_length=255)
    countrycode = models.CharField(max_length=255)
    state_province = models.CharField(max_length=255)
    county = models.CharField(max_length=255)
    municipality = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    species = models.ForeignKey(
        Species, on_delete=models.DO_NOTHING, related_name="observations")
    observer = models.ForeignKey(
        GbifObserver, on_delete=models.DO_NOTHING, related_name="observations")

    class Meta:
        indexes = [
            models.Index(fields=['species', 'latitude', 'longitude', 'public'],
                         name='obs_gbifobs_sp_lat_lon_pub_idx'),
            models.Index(fields=['observer'],
                         name='obs_gbifobs_observer_idx'),
        ]


class GbifObservationImage(models.Model):
    imgid = models.IntegerField()
    external_url = models.URLField()
    rights_holder = models.CharField(max_length=255)
    creator = models.CharField(max_length=255)
    license = models.CharField(max_length=255)
    is_thumbnail = models.BooleanField(default=False)
    observation = models.ForeignKey(
        GbifObservations, on_delete=models.CASCADE, related_name="images")
