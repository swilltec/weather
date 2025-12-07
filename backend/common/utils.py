
from ipware import get_client_ip

def get_ip(request):
    client_ip, _ = get_client_ip(request)
    return client_ip
