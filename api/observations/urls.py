from django.urls import path, include
from rest_framework.routers import DefaultRouter
from observations import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'observation', views.ObserverViewSet)
router.register(r'observer', views.ObserverViewSet)
router.register(r'image', views.ObservationImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
