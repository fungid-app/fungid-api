from django.urls import path, include
from rest_framework.routers import DefaultRouter
from taxonomy import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'species', views.SpeciesViewSet)
router.register(r'commonname', views.CommonNameViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
