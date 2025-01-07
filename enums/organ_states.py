from enum import StrEnum


class OrganState(StrEnum):
    HEALTHY = "Healthy"
    VACCINATED = "Vaccinated"
    INFECTED = "Infected"
    IMMUNISED = "Immunised"
