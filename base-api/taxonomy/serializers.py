from rest_framework import serializers
from taxonomy.models import Species


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = [
            'id',
            'phylum',
            'classname',
            'order',
            'family',
            'genus',
            'species',
            'description',
            'included_in_classifier',
            'number_of_observations',
            'common_names',
        ]


class CommonNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['id', 'name', 'species']
