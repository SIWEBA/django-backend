from rest_framework import serializers
from .models import Estacion, Lectura, TelemetriaDispositivo

class EstacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estacion
        fields = '__all__'

class LecturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lectura
        fields = '__all__'

class TelemetriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetriaDispositivo
        fields = '__all__'