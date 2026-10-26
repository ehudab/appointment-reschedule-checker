from fastapi import FastAPI
from pydantic import BaseModel, Field


from geo import get_lat_lon
from weather import get_weather_full


class Appointment(BaseModel):
    date: str = Field(..., title="Date of the appointment", max_length=100)
    time: str = Field(..., title="Time of the appointment", max_length=100)
    location: str = Field(..., title="Location of the appointment", max_length=100)




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
    loc = get_lat_lon(appointment.location)

    lat = loc.get("latitude")
    lon = loc.get("longitude")

    # Do not request weather until the location has been successfully geocoded.
    if lat is None or lon is None:
        return {"error": loc.get("error", "Location could not be geocoded.")}

    weather = get_weather_full(lat, lon)
    main_weather = weather.get("weather", [])[0].get("main")
    # Pass API failures back to the caller instead of making a decision from missing data.
    if "error" in weather:
        return weather

    return {
        "date": appointment.date,
        "time": appointment.time,
        "main_weather": main_weather,
        "verdict": appointment_verdict(weather),
    }