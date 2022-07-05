from rest_framework import serializers
from observations.models import GbifObservations, GbifObservationImage, GbifObserver


class GbifObserverSerializer(serializers.ModelSerializer):
    class Meta:
        model = GbifObserver
        fields = ['id', 'name']


class GbifObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GbifObservations
        fields = ['gbifid', 'date', 'latitude', 'longitude', 'public', 'acces_rights', 'rights_holder',
                  'recorded_by', 'license', 'countrycode', 'state_province', 'county', 'municipality',
                  'locality', 'species', 'observer']


class GbifObservationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GbifObservationImage
        fields = ['id', 'imgid', 'external_url', 'rights_holder',
                  'creator', 'license', 'is_thumbnail', 'gbifid']
