export const API_CONFIG = {
    // Using v2.5 endpoints for current weather and 5-day forecast (more widely available than 3.0)
    BASE_URL: "https://api.openweathermap.org/data/2.5",
    GEO: "https://api.openweathermap.org/geo/1.0",
    API_KEY: import.meta.env.VITE_OPENWEATHER_API_KEY,
    DEFAULT_PARAMS: {
        units: "metric",
        appid: import.meta.env.VITE_OPENWEATHER_API_KEY,
    },
};
