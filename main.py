from datetime import datetime, timedelta
from enum import Enum

from astrolog import GeoLocation, NatalObject, Planet
from fastapi import FastAPI

app = FastAPI()

GeoLocation.PLACES = {
    "Zaporozhye": GeoLocation("47n50", "35e10"),
    "Mariupol": GeoLocation("47n08", "37e34"),
    "Sukhumi": GeoLocation("43n00", "41e01"),
    "Odessa": GeoLocation("46n28", "30e44"),
    "Kyiv": GeoLocation("50n27", "30e30"),
    "Zug": GeoLocation("47n10", "8e31")
}


class TimeStep(Enum):
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    YEARS = "years"

    def timedelta(self, n: int) -> timedelta:
        if self is TimeStep.HOURS:
            return timedelta(hours=n)
        elif self is TimeStep.DAYS:
            return timedelta(days=n)
        elif self is TimeStep.WEEKS:
            return timedelta(weeks=n)
        elif self is TimeStep.YEARS:
            return timedelta(days=n*365)
        else:
            raise ValueError("unknown enum value")


@app.get("/{planet_name}/topo/{place}/pos/{date}")
async def planet_pos(planet_name: str, place: str, date: datetime):
    location = GeoLocation.PLACES.get(place.capitalize())
    if location is None:
        raise NameError(place)
    planet = Planet(planet_name)
    coord = planet.equator_speed(date, location)
    return coord.json()


@app.get("/{planet_name}/topo/{place}/{time_step}/{time_delta}/{start}/{till}/pos/{date}")
async def planet_path(planet_name: str, place: str, time_step: TimeStep, time_delta: int, start: datetime, till: datetime, date: datetime):
    location = GeoLocation.PLACES.get(place.capitalize())
    coord = await planet_pos(planet_name, place, date)
    planet = Planet(planet_name)
    path = []

    delta = time_step.timedelta(time_delta)
    dt = start
    while dt < till:
        json = planet.equator_speed(dt, location).json()
        json['ts'] = dt
        path.append(json)
        dt += delta
    return {"coord": coord, "path": path}
