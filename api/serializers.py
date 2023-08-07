from rest_framework import serializers
from .models import Query, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("ip",)


class QuerySerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True)

    class Meta:
        model = Query
        fields = ("client_ip", "created_at", "domain", "addresses")


class HTTPErrorSerializer(serializers.Serializer):
    message = serializers.CharField()


class ValidateIPResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
