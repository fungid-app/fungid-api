from rest_framework import viewsets
from taxonomy.models import Species, CommonNames
from taxonomy.serializers import SpeciesSerializer, CommonNamesSerializer


class SpeciesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer


class CommonNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommonNames.objects.all()
    serializer_class = CommonNamesSerializer
