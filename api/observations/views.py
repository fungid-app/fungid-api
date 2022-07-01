from rest_framework import viewsets
from observations.models import Observations, ObservationImage, Observer
from observations.serializers import ObserverSerializer, ObservationSerializer, ObservationImageSerializer


class ObserverViewSet(viewsets.ModelViewSet):
    queryset = Observer.objects.all()
    serializer_class = ObserverSerializer


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = Observations.objects.all()
    serializer_class = ObservationSerializer


class ObservationImageViewSet(viewsets.ModelViewSet):
    queryset = ObservationImage.objects.all()
    serializer_class = ObservationImageSerializer
