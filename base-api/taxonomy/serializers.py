from rest_framework import serializers
from taxonomy.models import Phylum, ClassTax, Order, Family, Genus, Species


class PhylumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phylum
        fields = ['id', 'name', 'key']


class ClassTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTax
        fields = ['id', 'name', 'key', 'phylum']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'name', 'key', 'classtax']


class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ['id', 'name', 'key', 'order']


class GenusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genus
        fields = ['id', 'name', 'key', 'family']


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['id', 'name', 'key', 'genus', 'included_in_classifier']


class CommonNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['id', 'name', 'species']
