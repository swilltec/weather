from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings


class Units(Enum):
    """Enum for units of measurement."""

    STANDARD = "standard"  # Kelvin
    METRIC = "metric"  # Celsius
    IMPERIAL = "imperial"  # Fahrenheit


class OpenWeatherService:
    """
    Service class for OpenWeather FREE API endpoints.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "https://api.openweathermap.org/geo/1.0"

    def __init__(self, api_key: str = settings.WEATHER_API):
        self.api_key = api_key
        self.session = requests.Session()

    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the OpenWeather API."""
        params["appid"] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("Invalid API key")
            elif response.status_code == 404:
                raise Exception("Location not found")
            elif response.status_code == 429:
                raise Exception("API rate limit exceeded")
            else:
                error_msg = (
                    response.json().get("message", str(e)) if response.text else str(e)
                )
                raise Exception(f"API request failed: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {e}")

    def get_current_weather(
        self, location: str, units: str = "metric"
    ) -> Dict[str, Any]:
        """Get current weather by city name."""
        url = f"{self.BASE_URL}/weather"
        params = {"q": location, "units": units}

        data = self._make_request(url, params)

        return {
            "location": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "weather": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg"),
            "clouds": data["clouds"]["all"],
            "visibility": data.get("visibility"),
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime(
                "%H:%M:%S"
            ),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime(
                "%H:%M:%S"
            ),
            "timezone": data["timezone"],
            "units": units,
        }

    def get_forecast(
        self, location: str, days: int = 5, units: str = "metric"
    ) -> Dict[str, Any]:
        """Get 5-day forecast (3-hour intervals)."""
        url = f"{self.BASE_URL}/forecast"
        params = {"q": location, "units": units}

        data = self._make_request(url, params)

        # Process forecast data
        forecasts = []
        for item in data["list"][: days * 8]:  # 8 forecasts per day (3-hour intervals)
            forecasts.append(
                {
                    "datetime": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "temp_min": item["main"]["temp_min"],
                    "temp_max": item["main"]["temp_max"],
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "weather": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"],
                    "clouds": item["clouds"]["all"],
                    "pop": item.get("pop", 0) * 100,  # Probability of precipitation
                }
            )

        return {
            "location": data["city"]["name"],
            "country": data["city"]["country"],
            "forecasts": forecasts,
            "units": units,
        }

    def get_coordinates(self, location: str) -> Dict[str, Any]:
        """Get coordinates for a location."""
        url = f"{self.GEO_URL}/direct"
        params = {"q": location, "limit": 1}

        data = self._make_request(url, params)

        if not data:
            raise Exception("Location not found")

        return {
            "name": data[0]["name"],
            "latitude": data[0]["lat"],
            "longitude": data[0]["lon"],
            "country": data[0].get("country"),
            "state": data[0].get("state"),
        }

    def get_weather_by_coordinates(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> Dict[str, Any]:
        """Get current weather by coordinates."""
        url = f"{self.BASE_URL}/weather"
        params = {"lat": latitude, "lon": longitude, "units": units}

        data = self._make_request(url, params)

        return {
            "location": data["name"],
            "country": data["sys"]["country"],
            "latitude": latitude,
            "longitude": longitude,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "weather": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "units": units,
        }

    def get_air_pollution(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get air quality data by coordinates."""
        url = f"{self.BASE_URL}/air_pollution"
        params = {"lat": latitude, "lon": longitude}

        data = self._make_request(url, params)

        aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}

        components = data["list"][0]["components"]

        return {
            "latitude": latitude,
            "longitude": longitude,
            "aqi": data["list"][0]["main"]["aqi"],
            "aqi_level": aqi_levels.get(data["list"][0]["main"]["aqi"], "Unknown"),
            "co": components.get("co"),
            "no": components.get("no"),
            "no2": components.get("no2"),
            "o3": components.get("o3"),
            "so2": components.get("so2"),
            "pm2_5": components.get("pm2_5"),
            "pm10": components.get("pm10"),
            "nh3": components.get("nh3"),
        }
