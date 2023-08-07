from django.urls import path
from .views import (
    HistoryView,
    ToolsLookupView,
    ToolsValidateView,
    RootView,
    HealthView,
    MetricsView,
)

urlpatterns = [
    path("", RootView.as_view(), name="root"),
    path("health", HealthView.as_view(), name="health"),
    path("metrics", MetricsView.as_view(), name="metrics"),
    path("history", HistoryView.as_view(), name="queries-history"),
    path("tools/lookup", ToolsLookupView.as_view(), name="lookup-domain"),
    path("tools/validate", ToolsValidateView.as_view(), name="validate-ip"),
]
