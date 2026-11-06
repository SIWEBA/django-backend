from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from .models import Estacion, Lectura, Subestacion, TelemetriaDispositivo
from .serializers import (
    EstacionSerializer,
    LecturaSerializer,
    SubestacionSerializer,
    TelemetriaSerializer,
)

class EstacionViewSet(viewsets.ModelViewSet):
    queryset = Estacion.objects.all()
    serializer_class = EstacionSerializer


class SubestacionViewSet(viewsets.ModelViewSet):
    queryset = Subestacion.objects.select_related('estacion')
    serializer_class = SubestacionSerializer


class LecturaViewSet(viewsets.ModelViewSet):
    queryset = Lectura.objects.all()
    serializer_class = LecturaSerializer
    throttle_scope = 'lecturas'
    lookup_value_regex = r'[^/]+'

    def get_object(self):
        station_id, separator, timestamp = self.kwargs['pk'].partition(',')
        parsed_timestamp = parse_datetime(timestamp) if separator else None
        if not station_id.isdecimal() or parsed_timestamp is None:
            raise NotFound('Use el formato <estacion_id>,<fecha_hora ISO-8601>.')

        obj = get_object_or_404(
            self.filter_queryset(self.get_queryset()),
            estacion_id=station_id,
            fecha_hora=parsed_timestamp,
        )
        self.check_object_permissions(self.request, obj)
        return obj

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
    lookup_value_regex = r'[^/]+'

    def get_object(self):
        substation_id, separator, timestamp = self.kwargs['pk'].partition(',')
        parsed_timestamp = parse_datetime(timestamp) if separator else None
        if not substation_id.isdecimal() or parsed_timestamp is None:
            raise NotFound('Use el formato <subestacion_id>,<fecha_hora ISO-8601>.')

        obj = get_object_or_404(
            self.filter_queryset(self.get_queryset()),
            subestacion_id=substation_id,
            fecha_hora=parsed_timestamp,
        )
        self.check_object_permissions(self.request, obj)
        return obj