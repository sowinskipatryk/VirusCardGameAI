from abc import ABC, abstractmethod

from enums import OrganState


class OrganStateHandler(ABC):
    @abstractmethod
    def apply_virus(self, organ, virus):
        pass

    @abstractmethod
    def apply_medicine(self, organ, medicine):
        pass


class HealthyStateHandler(OrganStateHandler):
    state = OrganState.HEALTHY

    def apply_virus(self, organ, virus):
        organ.state_handler = InfectedStateHandler()

    def remove_virus(self, organ, virus):
        raise ValueError('Virus cannot be removed from healthy organ')

    def apply_medicine(self, organ, medicine):
        organ.state_handler = VaccinatedStateHandler()

    def remove_medicine(self, organ, medicine):
        raise ValueError('Medicine cannot be removed from healthy organ')


class InfectedStateHandler(OrganStateHandler):
    state = OrganState.INFECTED

    def apply_virus(self, organ, virus):
        organ.state_handler = HealthyStateHandler()  # reset to default state before discarding the organ

    def remove_virus(self, organ, virus):
        organ.state_handler = HealthyStateHandler()

    def apply_medicine(self, organ, medicine):
        organ.state_handler = HealthyStateHandler()

    def remove_medicine(self, organ, medicine):
        raise ValueError('Medicine cannot be removed from infected organ')


class VaccinatedStateHandler(OrganStateHandler):
    state = OrganState.VACCINATED

    def apply_virus(self, organ, virus):
        organ.state_handler = HealthyStateHandler()

    def remove_virus(self, organ, virus):
        raise ValueError('Virus cannot be removed from vaccinated organ')

    def apply_medicine(self, organ, medicine):
        organ.state_handler = ImmunisedStateHandler()

    def remove_medicine(self, organ, medicine):
        organ.state_handler = HealthyStateHandler()


class ImmunisedStateHandler(OrganStateHandler):
    state = OrganState.IMMUNISED

    def apply_virus(self, organ, virus):
        raise ValueError('Virus cannot be applied on immunised organ')

    def remove_virus(self, organ, virus):
        raise ValueError('Virus cannot be removed from immunised organ')

    def apply_medicine(self, organ, medicine):
        raise ValueError('Medicine cannot be applied on immunised organ')

    def remove_medicine(self, organ, medicine):
        raise ValueError('Medicine cannot be removed from immunised organ')
