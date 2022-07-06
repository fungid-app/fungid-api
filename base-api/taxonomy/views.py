from rest_framework import viewsets
from taxonomy.models import Species, CommonNames
from taxonomy.serializers import SpeciesSerializer, CommonNamesSerializer
from rest_framework.response import Response


class SpeciesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer

    def retrieve(self, request, *args, **kwargs):
        if kwargs['pk'].isdigit():
            return super().retrieve(request, *args, **kwargs)
        else:
            value = Species.objects.get(species=kwargs['pk'])
            serialzer = SpeciesSerializer(value)
            return Response(serialzer.data)


class CommonNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommonNames.objects.all()
    serializer_class = CommonNamesSerializer
