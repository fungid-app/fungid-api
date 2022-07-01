from django.db import models
from django.db.models.functions import Lower


class Phylum(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'), name='phylum_unique_name')
        ]
    name = models.CharField(max_length=255, unique=True)
    key = models.IntegerField()


class ClassTax(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), name='class_unique_name')
        ]
    name = models.CharField(max_length=255, unique=True)
    key = models.IntegerField()
    phylum = models.ForeignKey(
        Phylum, on_delete=models.DO_NOTHING, related_name='subclasses')


class Order(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), name='order_unique_name')
        ]
    name = models.CharField(max_length=255, unique=True)
    key = models.IntegerField()
    classtax = models.ForeignKey(
        ClassTax, on_delete=models.DO_NOTHING, related_name="suborders")


class Family(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), name='family_unique_name')
        ]
    name = models.CharField(max_length=255, unique=True)
    key = models.IntegerField()
    order = models.ForeignKey(
        Order, on_delete=models.DO_NOTHING, related_name="subfamilies")


class Genus(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), name='genus_unique_name')
        ]
    name = models.CharField(max_length=255, unique=True)
    key = models.IntegerField()
    family = models.ForeignKey(
        Family, on_delete=models.DO_NOTHING, related_name="subgenera")


class Species(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('name'), name='species_unique_name')
        ]
    name = models.CharField(max_length=100, unique=True)
    key = models.IntegerField()
    description = models.TextField()
    included_in_classifier = models.BooleanField(default=False)
    genus = models.ForeignKey(
        Genus, on_delete=models.DO_NOTHING, related_name="subspecies")


class CommonNames(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'), 'species', name='commonnames_unique_name')
        ]
    name = models.CharField(max_length=255, unique=True)
    species = models.ForeignKey(
        Species, on_delete=models.DO_NOTHING, related_name="common_names")
