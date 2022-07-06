from rest_framework import viewsets
from observations.models import GbifObservations, GbifObservationImage, GbifObserver
from observations.serializers import GbifObserverSerializer, GbifObservationSerializer, GbifObservationImageSerializer


class ObserverViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GbifObserver.objects.all()
    serializer_class = GbifObserverSerializer


class ObservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GbifObservations.objects.all()
    serializer_class = GbifObservationSerializer


class ObservationImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GbifObservationImage.objects.all()
    serializer_class = GbifObservationImageSerializer
