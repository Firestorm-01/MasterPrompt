"""
Weather tool - OpenWeatherMap.
"""
import os
from tools.base import BaseTool
class WeatherTool(BaseTool):
    name = "weather"
    description = """Get current weather and forecast.
    Actions: 'current' (city), 'forecast' (city)"""
    category = "Web & Research"
    required_env_vars = ["OPENWEATHERMAP_API_KEY"]
    is_free = True
    def is_available(self) -> bool:
        return bool(os.getenv("OPENWEATHERMAP_API_KEY"))
    def _run(self, action: str = "current", city: str = None, **kwargs) -> str:
        import httpx
        if not city:
            return "Error: 'city' parameter required"
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        with httpx.Client() as client:
            if action == "current":
                resp = client.get("https://api.openweathermap.org/data/2.5/weather", params={"q": city, "appid": api_key, "units": "metric"})
                data = resp.json()
                if data.get("cod") != 200:
                    return f"City not found: {city}"
                return f"Weather in {data['name']}:\nTemperature: {data['main']['temp']}°C\nConditions: {data['weather'][0]['description'].title()}\nHumidity: {data['main']['humidity']}%"
            elif action == "forecast":
                resp = client.get("https://api.openweathermap.org/data/2.5/forecast", params={"q": city, "appid": api_key, "units": "metric"})
                data = resp.json()
                seen = set()
                output = [f"Forecast for {city}:"]
                for item in data["list"]:
                    date = item["dt_txt"][:10]
                    if date not in seen and len(seen) < 5:
                        seen.add(date)
                        output.append(f"{date}: {item['main']['temp']}°C - {item['weather'][0]['description']}")
                return "\n".join(output)
        return f"Error: Unknown action '{action}'"
