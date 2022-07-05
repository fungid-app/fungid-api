from django.db import models
from django.db.models.functions import Lower


class Species(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('species'), name='taxonomy_species_unique_name')
        ]

    phylum = models.CharField(max_length=255, null=True)
    classname = models.CharField(max_length=255, null=True)
    order = models.CharField(max_length=255, null=True)
    family = models.CharField(max_length=255, null=True)
    genus = models.CharField(max_length=255, null=True)
    species = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    included_in_classifier = models.BooleanField(default=False)
    number_of_observations = models.IntegerField()


class CommonNames(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'), 'language', 'species', name='taxonomy_commonnames_unique_name')
        ]
        indexes = [
            models.Index(fields=['species', 'language'],
                         name='taxonomy_cn_species_lang_idx'),
        ]

    name = models.CharField(max_length=255)
    species = models.ForeignKey(
        Species, on_delete=models.DO_NOTHING, related_name="common_names")
    language = models.CharField(max_length=5, null=True)
