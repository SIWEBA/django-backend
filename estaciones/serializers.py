from rest_framework import serializers
from .models import Estacion, Lectura, Subestacion, TelemetriaDispositivo

class EstacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estacion
        fields = '__all__'


class SubestacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subestacion
        fields = '__all__'


class LecturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lectura
        exclude = ('pk',)

class TelemetriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetriaDispositivo
        exclude = ('pk',)