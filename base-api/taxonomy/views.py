from rest_framework import viewsets
from taxonomy.models import Phylum, ClassTax, Order, Family, Genus, Species, CommonNames
from taxonomy.serializers import PhylumSerializer, ClassTaxSerializer, OrderSerializer, FamilySerializer, GenusSerializer, SpeciesSerializer, CommonNamesSerializer


class PhylumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Phylum.objects.all()
    serializer_class = PhylumSerializer


class ClassTaxViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClassTax.objects.all()
    serializer_class = ClassTaxSerializer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class FamilyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer


class GenusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genus.objects.all()
    serializer_class = GenusSerializer


class SpeciesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer


class CommonNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommonNames.objects.all()
    serializer_class = CommonNamesSerializer
