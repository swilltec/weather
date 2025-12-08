from django.core.cache import cache


def get_weather(latitude, longitude, ttl=600):
    """
    Retrieve current weather data for the given coordinates, with caching.

    This function checks a cache for previously fetched weather data
    associated with the (latitude, longitude) pair. If the data is not
    present or has expired, it fetches fresh data from the weather API
    and stores it in the cache.

    Args:
        latitude (float): Geographic latitude of the location.
        longitude (float): Geographic longitude of the location.
        ttl (int, optional): Cache lifetime in seconds. Defaults to 600 (10 minutes).

    Returns:
        dict: Weather information returned by the weather API.
    """
    cache_key = f"weather:{latitude}:{longitude}"
    weather_data = cache.get(cache_key)

    if weather_data is None:
        weather_data = fetch_from_weather_api(latitude, longitude)
        cache.set(cache_key, weather_data, timeout=ttl)

    return weather_data


def get_weather_alerts(latitude, longitude, ttl=600):
    """
    Retrieve weather alerts for the given coordinates, with caching.

    Weather alerts tend to change more frequently than general weather data,
    so they are cached for a short period (default 10 minutes). The function
    first attempts to read alerts from the cache, and if none are found,
    fetches them from the alerts API and stores them in the cache.

    Args:
        latitude (float): Geographic latitude of the location.
        longitude (float): Geographic longitude of the location.
        ttl (int, optional): Cache lifetime in seconds. Defaults to 600 (10 minutes).

    Returns:
        dict or list: Weather alerts returned by the alerts API.
    """
    cache_key = f"alerts:{latitude}:{longitude}"
    alerts = cache.get(cache_key)

    if alerts is None:
        alerts = fetch_alerts_from_api(latitude, longitude)
        cache.set(cache_key, alerts, timeout=ttl)

    return alerts
