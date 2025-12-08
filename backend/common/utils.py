from django.contrib.gis.geoip2 import GeoIP2
from ipware import get_client_ip

# Initiaate once
geo_ip = GeoIP2()


def get_ip(request):
    client_ip, _ = get_client_ip(request)
    return client_ip


def get_city(request):
    client_ip = get_client_ip(request)
    geo_ip.city(client_ip)


def is_united_states(city):
    return city.get("country_code", "") == "US"
