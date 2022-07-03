from django.urls import path, include
from rest_framework.routers import DefaultRouter
from taxonomy import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'phylum', views.PhylumViewSet)
router.register(r'class', views.ClassTaxViewSet)
router.register(r'order', views.OrderViewSet)
router.register(r'family', views.FamilyViewSet)
router.register(r'genus', views.GenusViewSet)
router.register(r'species', views.SpeciesViewSet)
router.register(r'commonname', views.CommonNameViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
