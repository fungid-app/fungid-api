from rest_framework import serializers
from observations.models import Observations, ObservationImage, Observer


class ObserverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observer
        fields = ['id', 'name']


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observations
        fields = ['id', 'date', 'latitude', 'longitude',
                  'public', 'species', 'observer', 'images']


class ObservationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationImage
        fields = ['id', 'url', 'observation']
