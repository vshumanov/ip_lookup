import os
import socket
import time
from ipaddress import IPv4Address, ip_address

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from prometheus_client import generate_latest
from rest_framework import status, views
from rest_framework.response import Response

from .metrics import active_users, http_requests_total, response_time
from .models import Address, Query
from .serializers import (
    HTTPErrorSerializer,
    QuerySerializer,
    ValidateIPResponseSerializer,
)
from .utils import get_client_ip, perform_domain_lookup


class RootView(views.APIView):
    @swagger_auto_schema(operation_description="Return time, version and k8s status")
    def get(self, request):
        version = "0.1.0"  # TODO shouldn't be hardcoded
        date = int(time.time())
        kubernetes = (
            os.environ.get("KUBERNETES_SERVICE_HOST") is not None
        )  # A bit simplistic but can be expanded in a later time
        return Response({"version": version, "date": date, "kubernetes": kubernetes})


class HealthView(views.APIView):
    @swagger_auto_schema(operation_description="health check")
    def get(self, request):
        return Response({"status": "healthy"})


class MetricsView(views.APIView):
    @swagger_auto_schema(operation_description="metrics for prometheus")
    def get(self, request):
        # Example Values for response time and active_users
        http_requests_total.labels(method=request.method).inc()
        response_time.labels(method=request.method).observe(0.5)
        active_users.set(42)

        content = generate_latest()
        return Response(content, content_type="text/plain")


class HistoryView(views.APIView):
    @swagger_auto_schema(
        operation_description="List last 20 queries",
        responses={
            200: QuerySerializer(many=True),
            400: HTTPErrorSerializer(),
            500: HTTPErrorSerializer(),
        },
    )
    def get(self, request):
        queries = Query.objects.all().order_by("-created_at")[:20]
        serializer = QuerySerializer(queries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ToolsLookupView(views.APIView):
    @swagger_auto_schema(
        operation_description="Lookup domain and return all IPv4 addresses",
        manual_parameters=[
            openapi.Parameter(
                "domain",
                openapi.IN_QUERY,
                description="Domain name",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: QuerySerializer(),
            400: HTTPErrorSerializer(),
            404: HTTPErrorSerializer(),
        },
        tags=["tools"],
    )
    def get(self, request):
        domain = request.query_params.get("domain")
        client_ip = get_client_ip(request)

        addresses = perform_domain_lookup(domain)
        if not addresses:
            error_serializer = HTTPErrorSerializer(
                data={"message": "Domain not found."}
            )
            if error_serializer.is_valid():
                return Response(error_serializer.data, status=status.HTTP_404_NOT_FOUND)

        query = Query.objects.create(domain=domain, client_ip=client_ip)
        query.save()
        address_instances = [Address(ip=ip, query=query) for ip in addresses]
        Address.objects.bulk_create(address_instances)

        query_data = {
            "domain": domain,
            "client_ip": client_ip,
            "addresses": [{"ip": ip} for ip in addresses],
        }
        serializer = QuerySerializer(data=query_data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToolsValidateView(views.APIView):
    @swagger_auto_schema(
        operation_description="Simple IP validation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"ip": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={200: ValidateIPResponseSerializer(), 400: HTTPErrorSerializer()},
        tags=["tools"],
    )
    def post(self, request):
        ip = request.data.get("ip")
        try:
            serializer = ValidateIPResponseSerializer(
                data={"status": True if type(ip_address(ip)) is IPv4Address else False}
            )
        except ValueError:
            serializer = HTTPErrorSerializer(data={"message": "Invalid IP provided."})
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
