from rest_framework import serializers
from observations.models import GbifObservations, GbifObservationImage, GbifObserver


class GbifObserverSerializer(serializers.HyperlinkedModelSerializer):
    observations = serializers.HyperlinkedRelatedField(
        many=True, view_name='observation-detail', read_only=True)

    class Meta:
        model = GbifObserver
        fields = ['id', 'name']


class GbifObservationSerializer(serializers.HyperlinkedModelSerializer):
    images = serializers.HyperlinkedRelatedField(
        many=True, view_name='image-detail', read_only=True)

    class Meta:
        model = GbifObservations
        fields = ['gbifid', 'datecreated', 'latitude', 'longitude', 'public', 'acces_rights', 'rights_holder',
                  'recorded_by', 'license', 'countrycode', 'state_province', 'county', 'municipality',
                  'locality', 'species', 'observer', 'images']


class GbifObservationImageSerializer(serializers.HyperlinkedModelSerializer):
    observation = serializers.HyperlinkedRelatedField(
        view_name='observation-detail', read_only=True)

    class Meta:
        model = GbifObservationImage
        fields = ['id', 'imgid', 'external_url', 'rights_holder',
                  'creator', 'license', 'is_thumbnail', 'observation_id']
