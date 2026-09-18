from rest_framework.routers import DefaultRouter
from .views import EstacionViewSet, LecturaViewSet, TelemetriaViewSet

router = DefaultRouter()
router.register('estaciones', EstacionViewSet)
router.register('lecturas', LecturaViewSet)
router.register('telemetria', TelemetriaViewSet)

urlpatterns = router.urls