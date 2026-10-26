from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator


from geo import get_lat_lon
from weather import get_weather_full


class Appointment(BaseModel):
    date: str = Field(..., title="Date of the appointment", max_length=100)
    time: str = Field(..., title="Time of the appointment", max_length=100)
    appointment_location: str = Field(
        ..., title="Location of the appointment", max_length=100
    )

    @model_validator(mode="before")
    @classmethod
    def flatten_custom_data(cls, values):
        if not isinstance(values, dict):
            return values

        # GHL sends custom fields in customData, while root fields remain supported.
        custom_data = values.get("customData") or values.get("custom_data") or {}
        if not isinstance(custom_data, dict):
            custom_data = {}

        normalized = dict(custom_data)
        for field in ("date", "time", "appointment_location"):
            if field in values:
                normalized[field] = values[field]
        return normalized




app = FastAPI(title="Weather Check for Appointments")


def appointment_verdict(weather):
    conditions = weather.get("weather", [])
    condition_ids = [condition.get("id", 0) for condition in conditions]
    temperature = weather.get("main", {}).get("temp")
    wind_speed = weather.get("wind", {}).get("speed", 0)

    # OpenWeather IDs identify thunderstorms, heavy rain, snow, squalls, and tornadoes.
    severe_condition = any(
        200 <= condition_id <= 232
        or 502 <= condition_id <= 531
        or 600 <= condition_id <= 622
        or condition_id in {771, 781}
        for condition_id in condition_ids
    )
    extreme_temperature = temperature is not None and (
        temperature < 0 or temperature > 35
    )

    # Reschedule when outdoor conditions are dangerous or unusually uncomfortable.
    if severe_condition or extreme_temperature or wind_speed > 10:
        return "Consider rescheduling"
    return "Keep appointment"


@app.post("/appointments")
def check_weather(appointment: Appointment):
    loc = get_lat_lon(appointment.appointment_location)

    lat = loc.get("latitude")
    lon = loc.get("longitude")

    # Do not request weather until the location has been successfully geocoded.
    if lat is None or lon is None:
        return {"error": loc.get("error", "Location could not be geocoded.")}

    weather = get_weather_full(lat, lon)
    # Pass API failures back to the caller instead of making a decision from missing data.
    if "error" in weather:
        return weather

    conditions = weather.get("weather", [])
    main_weather = conditions[0].get("main") if conditions else None

    return {
        "date": appointment.date,
        "time": appointment.time,
        "main_weather": main_weather,
        "verdict": appointment_verdict(weather),
    }