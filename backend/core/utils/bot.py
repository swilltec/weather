import json
import os
from typing import Any, Callable, Dict, List, Optional

import openai
from django.conf import settings

from backend.core.utils.weather_api import OpenWeatherService


class WeatherAIService:
    """
    Weather AI service for Django - handles AI conversation without printing.
    Uses database for message persistence and per-user history.
    """

    WEATHER_SYSTEM_PROMPT = """You are a specialized weather assistant. Your ONLY purpose is to help users with weather-related questions and requests.

Weather-related topics include:
- Current weather conditions
- Weather forecasts
- Temperature, humidity, wind speed, precipitation
- Climate and seasonal patterns
- Weather phenomena (storms, hurricanes, snow, rain, etc.)
- UV index, air quality, visibility
- Weather safety and preparedness
- Historical weather data
- Weather impact on activities (outdoor events, travel, etc.)

If a user asks about ANYTHING that is NOT related to weather or the environment/climate, you must politely redirect them:
- Do NOT answer non-weather questions
- Politely explain you can only help with weather-related queries
- Suggest weather-related topics they might be interested in

Be friendly but firm about staying on topic.

When presenting weather data:
- Use clear, conversational language
- Include relevant details based on user's question
- Mention units (Celsius/Fahrenheit) when discussing temperature
- Provide context and practical advice when appropriate

You have access to real-time weather data through functions. Use them when users ask about current conditions, forecasts, or air quality."""

    def __init__(
        self,
        api_key: str = settings.POE_API_KEY,
        model: str = "claude-sonnet-4.5",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """Initialize the Weather AI service."""
        self.openai_api_key = api_key

        openai.api_key = self.openai_api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.weather_service = OpenWeatherService()

        # Function registry
        self.functions: Dict[str, Callable] = {}
        self.function_schemas: List[Dict[str, Any]] = []

        self._register_all_functions()

    def _register_all_functions(self):
        """Register all available weather functions."""

        self.register_function(
            func=self._get_current_weather_wrapper,
            name="get_current_weather",
            description="Get current weather conditions for any city or location worldwide.",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, optionally with country code (e.g., 'London', 'London,UK')",
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Units for temperature and wind speed",
                        "default": "metric",
                    },
                },
                "required": ["location"],
            },
        )

        self.register_function(
            func=self._get_forecast_wrapper,
            name="get_weather_forecast",
            description="Get weather forecast for upcoming days (up to 5 days) with 3-hour intervals.",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, optionally with country code",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast (1-5)",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 5,
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "description": "Units for temperature",
                        "default": "metric",
                    },
                },
                "required": ["location"],
            },
        )

        self.register_function(
            func=self._get_coordinates_wrapper,
            name="get_location_coordinates",
            description="Get geographic coordinates for any location.",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or location",
                    }
                },
                "required": ["location"],
            },
        )

        self.register_function(
            func=self._get_weather_by_coordinates_wrapper,
            name="get_weather_by_coordinates",
            description="Get current weather using latitude and longitude coordinates.",
            parameters={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate",
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "default": "metric",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        )

        self.register_function(
            func=self._get_air_quality_wrapper,
            name="get_air_quality",
            description="Get current air quality index and pollution levels for a location.",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or location",
                    }
                },
                "required": ["location"],
            },
        )

    def _get_current_weather_wrapper(
        self, location: str, units: str = "metric"
    ) -> Dict[str, Any]:
        try:
            return self.weather_service.get_current_weather(location, units)
        except Exception as e:
            return {"error": str(e), "location": location}

    def _get_forecast_wrapper(
        self, location: str, days: int = 5, units: str = "metric"
    ) -> Dict[str, Any]:
        try:
            return self.weather_service.get_forecast(location, days, units)
        except Exception as e:
            return {"error": str(e), "location": location}

    def _get_coordinates_wrapper(self, location: str) -> Dict[str, Any]:
        try:
            return self.weather_service.get_coordinates(location)
        except Exception as e:
            return {"error": str(e), "location": location}

    def _get_weather_by_coordinates_wrapper(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> Dict[str, Any]:
        try:
            return self.weather_service.get_weather_by_coordinates(
                latitude, longitude, units
            )
        except Exception as e:
            return {"error": str(e)}

    def _get_air_quality_wrapper(self, location: str) -> Dict[str, Any]:
        try:
            coords = self.weather_service.get_coordinates(location)
            return self.weather_service.get_air_pollution(
                coords["latitude"], coords["longitude"]
            )
        except Exception as e:
            return {"error": str(e), "location": location}

    def register_function(
        self, func: Callable, name: str, description: str, parameters: Dict[str, Any]
    ) -> None:
        """Register a function."""
        self.functions[name] = func
        self.function_schemas.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            }
        )

    def get_system_prompt(self) -> Dict[str, str]:
        """Get the system prompt message."""
        return {"role": "system", "content": self.WEATHER_SYSTEM_PROMPT}

    def generate_response(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a response from the AI.

        Returns:
            Dict containing:
                - response: str (the assistant's message)
                - tool_calls: List[Dict] (any function calls made)
                - tool_results: List[Dict] (results from function calls)
                - needs_continuation: bool (if more API calls needed)
        """
        api_params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        if self.max_tokens:
            api_params["max_tokens"] = self.max_tokens

        if self.function_schemas:
            api_params["tools"] = self.function_schemas

        response = openai.chat.completions.create(**api_params)
        message = response.choices[0].message

        result = {
            "response": message.content,
            "tool_calls": [],
            "tool_results": [],
            "needs_continuation": False,
            "message_obj": message,  # Full message object for saving
        }

        # Handle function calls
        if message.tool_calls:
            result["needs_continuation"] = True

            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                tool_call_data = {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": function_name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                result["tool_calls"].append(tool_call_data)

                # Execute function
                if function_name in self.functions:
                    function_result = self.functions[function_name](**function_args)

                    result["tool_results"].append(
                        {
                            "tool_call_id": tool_call.id,
                            "function_name": function_name,
                            "function_args": function_args,
                            "result": function_result,
                        }
                    )

        return result
