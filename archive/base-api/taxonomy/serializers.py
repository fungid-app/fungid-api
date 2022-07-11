from rest_framework import serializers
from taxonomy.models import Species, CommonNames


class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    common_names = serializers.HyperlinkedRelatedField(
        many=True, view_name='commonname-detail', read_only=True)

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


class CommonNamesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CommonNames
        fields = ['id', 'name', 'species', 'language']
