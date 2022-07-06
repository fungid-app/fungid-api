from django.urls import path, include
from rest_framework.routers import DefaultRouter
from observations import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'observation', views.ObservationViewSet,
                basename='observation')
router.register(r'observer', views.ObserverViewSet, basename='observer')
router.register(r'image', views.ObservationImageViewSet, basename='image')

urlpatterns = [
    path('', include(router.urls)),
]
