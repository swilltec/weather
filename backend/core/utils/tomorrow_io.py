import hashlib
import json

import requests
from django.core.cache import cache

# request per second, 25 per hour and 500 per day
class TomorrowIO:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.tomorrow.io/v4",
        cache_ttl: int = 300,
    ):
        self.api_key = api_key
        # If the provided url has appending slash, remove it
        self.base_url = base_url.rstrip("/")
        self.cache_ttl = cache_ttl

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------

    def _make_cache_key(self, method: str, endpoint: str, params=None, body=None):
        raw = json.dumps(
            {"method": method, "endpoint": endpoint, "params": params, "body": body},
            sort_keys=True,
        )
        return "tomorrowio:" + hashlib.md5(raw.encode()).hexdigest()

    def _request(self, method: str, endpoint: str, params=None, body=None):
        params = params or {}
        params["apikey"] = self.api_key

        key = self._make_cache_key(method, endpoint, params, body)
        cached = cache.get(key)
        if cached:
            return cached

        url = f"{self.base_url}{endpoint}"

        if method == "GET":
            r = requests.get(url, params=params)
        elif method == "POST":
            r = requests.post(url, params={"apikey": self.api_key}, json=body)
        elif method == "PUT":
            r = requests.put(url, params={"apikey": self.api_key}, json=body)
        elif method == "DELETE":
            r = requests.delete(url, params={"apikey": self.api_key})
        else:
            raise ValueError("Invalid HTTP method")

        data = {"status_code": r.status_code, "json": None}
        try:
            data["json"] = r.json()
        except:
            pass

        cache.set(key, data, timeout=self.cache_ttl)
        return data

    # ---------------------------------------------------------
    # TIMELINES
    # ---------------------------------------------------------

    def get_timelines_basic(
        self,
        location: list,
        fields: list,
        start_time: str,
        end_time: str,
        timesteps: list,
        units: str = "metric",
        timezone: str = "UTC",
    ):
        return self._request(
            "GET",
            "/timelines",
            params={
                "location": location,
                "fields": fields,
                "startTime": start_time,
                "endTime": end_time,
                "timesteps": timesteps,
                "units": units,
                "timezone": timezone,
            },
        )

    def get_timelines_advanced(
        self,
        start_time: str,
        end_time: str,
        fields: list,
        timesteps: list,
        location: dict | list,
        units: str = "metric",
        timezone: str = "UTC",
    ):
        body = {
            "startTime": start_time,
            "endTime": end_time,
            "fields": fields,
            "timesteps": timesteps,
            "location": location,
            "units": units,
            "timezone": timezone,
        }
        return self._request("POST", "/timelines", body=body)

    # ---------------------------------------------------------
    # HISTORICAL
    # ---------------------------------------------------------

    def get_historical(
        self,
        start_time: str,
        end_time: str,
        fields: list,
        timesteps: list,
        location: dict | list,
        units: str = "metric",
        timezone: str = "UTC",
    ):
        body = {
            "startTime": start_time,
            "endTime": end_time,
            "fields": fields,
            "timesteps": timesteps,
            "location": location,
            "units": units,
            "timezone": timezone,
        }
        return self._request("POST", "/historical", body=body)

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------

    def get_events_basic(self, location, insights: list, buffer_km: int = 1):
        return self._request(
            "GET",
            "/events",
            params={
                "location": location,
                "insights": insights,
                "buffer": buffer_km,
            },
        )

    def get_events_advanced(
        self, location: dict | list, insights: list, buffer_km: int = 1
    ):
        body = {"location": location, "insights": insights, "buffer": buffer_km}
        return self._request("POST", "/events", body=body)

    # ---------------------------------------------------------
    # ROUTE
    # ---------------------------------------------------------

    def get_route(
        self,
        start_time: str,
        legs: list,
        fields: list,
        timestep: str,
        units: str = "metric",
        timezone: str = "UTC",
    ):
        body = {
            "startTime": start_time,
            "legs": legs,
            "fields": fields,
            "timestep": timestep,
            "units": units,
            "timezone": timezone,
        }
        return self._request("POST", "/route", body=body)

    # ---------------------------------------------------------
    # MAP TILES
    # ---------------------------------------------------------

    def get_map_tile(self, zoom: int, x: int, y: int, field: str, time_format: str):
        return self._request(
            "GET",
            f"/map/tile/{zoom}/{x}/{y}/{field}/{time_format}",
        )

    # ---------------------------------------------------------
    # LOCATIONS
    # ---------------------------------------------------------

    def list_locations(self):
        return self._request("GET", "/locations")

    def get_location(self, location_id: str):
        return self._request("GET", f"/locations/{location_id}")

    def create_location(self, name: str, geometry: dict, tags: list | None = None):
        body = {"name": name, "geometry": geometry, "tags": tags or []}
        return self._request("POST", "/locations", body=body)

    def update_location(self, location_id: str, name: str):
        return self._request(
            "PUT",
            f"/locations/{location_id}",
            body={"name": name},
        )

    def delete_location(self, location_id: str):
        return self._request("DELETE", f"/locations/{location_id}")

    def add_location_tags(self, locations: list, tags: list):
        return self._request(
            "POST",
            "/locations/tags/add",
            body={"locations": locations, "tags": tags},
        )

    def remove_location_tags(self, locations: list, tags: list):
        return self._request(
            "POST",
            "/locations/tags/remove",
            body={"locations": locations, "tags": tags},
        )

    # ---------------------------------------------------------
    # INSIGHTS
    # ---------------------------------------------------------

    def list_insights(self):
        return self._request("GET", "/insights")

    def get_insight(self, insight_id: str):
        return self._request("GET", f"/insights/{insight_id}")

    def create_insight(self, name: str, conditions: dict):
        body = {"name": name, "conditions": conditions}
        return self._request("POST", "/insights", body=body)

    def update_insight(self, insight_id: str, name: str, conditions: dict):
        return self._request(
            "PUT",
            f"/insights/{insight_id}",
            body={"name": name, "conditions": conditions},
        )

    def delete_insight(self, insight_id: str):
        return self._request("DELETE", f"/insights/{insight_id}")

    # ---------------------------------------------------------
    # ALERTS
    # ---------------------------------------------------------

    def list_alerts(self):
        return self._request("GET", "/alerts")

    def get_alert(self, alert_id: str):
        return self._request("GET", f"/alerts/{alert_id}")

    def create_alert(
        self,
        name: str,
        insight: str,
        is_active: bool,
        notifications: list,
    ):
        body = {
            "name": name,
            "insight": insight,
            "isActive": is_active,
            "notifications": notifications,
        }
        return self._request("POST", "/alerts", body=body)

    def update_alert(
        self,
        alert_id: str,
        name: str,
        notifications: list,
    ):
        return self._request(
            "PUT",
            f"/alerts/{alert_id}",
            body={"name": name, "notifications": notifications},
        )

    def delete_alert(self, alert_id: str):
        return self._request("DELETE", f"/alerts/{alert_id}")

    def get_alert_locations(self, alert_id: str):
        return self._request("GET", f"/alerts/{alert_id}/locations")

    def link_locations_to_alert(self, alert_id: str, locations: list):
        return self._request(
            "POST",
            f"/alerts/{alert_id}/locations/link",
            body={"locations": locations},
        )

    def unlink_locations_from_alert(self, alert_id: str, locations: list):
        return self._request(
            "POST",
            f"/alerts/{alert_id}/locations/unlink",
            body={"locations": locations},
        )

    def activate_alert(self, alert_id: str):
        return self._request("POST", f"/alerts/{alert_id}/activate", body={})

    def deactivate_alert(self, alert_id: str):
        return self._request("POST", f"/alerts/{alert_id}/deactivate", body={})
