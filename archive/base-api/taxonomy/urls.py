from django.urls import path, include
from rest_framework.routers import DefaultRouter
from taxonomy import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'species', views.SpeciesViewSet, basename='species')
router.register(r'commonname', views.CommonNameViewSet, basename='commonname')

urlpatterns = [
    path('', include(router.urls)),
]
