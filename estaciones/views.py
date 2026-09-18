from rest_framework import viewsets
from .models import Estacion, Lectura, TelemetriaDispositivo
from .serializers import EstacionSerializer, LecturaSerializer, TelemetriaSerializer

class EstacionViewSet(viewsets.ModelViewSet):
    queryset = Estacion.objects.all()
    serializer_class = EstacionSerializer

class LecturaViewSet(viewsets.ModelViewSet):
    queryset = Lectura.objects.all()
    serializer_class = LecturaSerializer
    throttle_scope = 'lecturas'

    def get_queryset(self):
        qs = super().get_queryset()
        estacion_id = self.request.query_params.get('estacion')
        if estacion_id:
            qs = qs.filter(estacion_id=estacion_id)
        return qs

class TelemetriaViewSet(viewsets.ModelViewSet):
    queryset = TelemetriaDispositivo.objects.all()
    serializer_class = TelemetriaSerializer
    throttle_scope = 'lecturas'