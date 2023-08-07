import socket
from typing import Optional


def perform_domain_lookup(domain: str) -> Optional[list]:
    try:
        return [
            entry[4][0] for entry in socket.getaddrinfo(domain, None, socket.AF_INET)
        ]
    except socket.gaierror as e:
        return None


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
