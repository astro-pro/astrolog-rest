from datetime import datetime, timedelta
from enum import Enum

from astrolog import GeoLocation, Planet, SecondFocus, ApoApsis, AscNode, DscNode, PeriApsis
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


class Method(Enum):
    PLANET = "planet"
    SECOND_FOCUS = "second_focus"
    APO_APSIS = "apoapsis"
    PERI_APSIS = "periapsis"
    ASC_NODE = "ascending_node"
    DSC_NODE = "descending_node"

    def celestial(self, name: str):
        if self == Method.PLANET:
            return Planet(name)
        elif self == Method.SECOND_FOCUS:
            return SecondFocus(name)
        elif self == Method.APO_APSIS:
            return ApoApsis(name)
        elif self == Method.PERI_APSIS:
            return PeriApsis(name)
        elif self == Method.ASC_NODE:
            return AscNode(name)
        elif self == Method.DSC_NODE:
            return DscNode(name)
        else
            raise RuntimeError("unknown computation method")

    def compute(self, name: str, place: str, date: datetime):
        location = GeoLocation.PLACES.get(place.capitalize())
        if location is None:
            raise RuntimeError(f"unknown geographic location ${place}")
        celestial = self.celestial(name)
        coord = celestial.equator_speed(date, location)
        return { "celestial": name, "type": self, "place": place, "date": date, "position": coord.json() }


@app.get("/{planet_name}/topo/{place}/pos/{date}")
async def planet_pos(planet_name: str, place: str, date: datetime):
    return Method.PLANET.compute(planet_name, place, date)


@app.get("/{planet_name}/topo/{place}/second-focus/{date}")
async def bs_pos(planet_name: str, place: str, date: datetime):
    return Method.SECOND_FOCUS.compute(planet_name, place, date)


@app.get("/{planet_name}/topo/{place}/apoapsis/{date}")
async def apo_pos(planet_name: str, place: str, date: datetime):
    return Method.APO_APSIS.compute(planet_name, place, date)


@app.get("/{planet_name}/topo/{place}/peroapsis/{date}")
async def peri_pos(planet_name: str, place: str, date: datetime):
    return Method.PERI_APSIS.compute(planet_name, place, date)


@app.get("/{planet_name}/topo/{place}/asc-node/{date}")
async def asc_pos(planet_name: str, place: str, date: datetime):
    return Method.ASC_NODE.compute(planet_name, place, date)


@app.get("/{planet_name}/topo/{place}/dsc-node/{date}")
async def dsc_pos(planet_name: str, place: str, date: datetime):
    return Method.DSC_NODE.compute(planet_name, place, date)


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
