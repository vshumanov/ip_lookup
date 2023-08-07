from prometheus_client import Counter, Histogram, Gauge

http_requests_total = Counter("http_requests_total", "Total HTTP requests", ["method"])
response_time = Histogram(
    "http_response_time_seconds", "HTTP response time", ["method"]
)
active_users = Gauge("active_users", "Active users")
