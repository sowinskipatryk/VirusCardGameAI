from abc import ABC, abstractmethod


class OrganState(ABC):
    @abstractmethod
    def apply_virus(self, organ, virus):
        pass

    @abstractmethod
    def apply_medicine(self, organ, medicine):
        pass


class HealthyState(OrganState):
    def apply_virus(self, organ, virus):
        organ.state = InfectedState()

    def apply_medicine(self, organ, medicine):
        organ.state = VaccinatedState()


class InfectedState(OrganState):
    def apply_virus(self, organ, virus):
        organ.state = HealthyState()  # reset to default state before discarding the organ

    def apply_medicine(self, organ, medicine):
        organ.state = HealthyState()


class VaccinatedState(OrganState):
    def apply_virus(self, organ, virus):
        organ.state = HealthyState()

    def apply_medicine(self, organ, medicine):
        organ.state = ImmunisedState()


class ImmunisedState(OrganState):
    def apply_virus(self, organ, virus):
        raise ValueError('Virus cannot be applied on immunised organ')

    def apply_medicine(self, organ, medicine):
        raise ValueError('Medicine cannot be applied on immunised organ')
