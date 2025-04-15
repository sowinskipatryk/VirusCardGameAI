from abc import ABC, abstractmethod

from enums import OrganState, CardColor


class OrganStateHandler(ABC):
    @abstractmethod
    def apply_virus(self, organ, virus):
        pass

    @abstractmethod
    def remove_virus(self, organ, virus):
        pass

    @abstractmethod
    def apply_medicine(self, organ, medicine):
        pass

    @abstractmethod
    def remove_medicine(self, organ, medicine):
        pass

    @abstractmethod
    def on_virus_play(self, virus_card, target_organ, target_player, owner, game_state):
        pass

    @abstractmethod
    def on_medicine_play(self, medicine_card, target_organ, game_state):
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

    def on_virus_play(self, virus_card, target_organ, target_player, owner, game_state):
        target_organ.add_virus(virus_card)
        if target_organ.color == CardColor.WILD:
            target_organ.color = virus_card.color

    def on_medicine_play(self, medicine_card, target_organ, game_state):
        target_organ.add_medicine(medicine_card)
        if target_organ.color == CardColor.WILD:
            target_organ.color = medicine_card.color


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

    def on_virus_play(self, virus_card, target_organ, target_player, owner, game_state):
        target_player.remove_organ_from_body(target_organ)
        target_organ.discard(game_state)
        game_state.add_card_to_discard_pile(virus_card)

    def on_medicine_play(self, medicine_card, target_organ, game_state):
        virus_card = target_organ.remove_virus()
        game_state.add_card_to_discard_pile(virus_card)
        game_state.add_card_to_discard_pile(medicine_card)
        target_organ.reset_wild_card()


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

    def on_virus_play(self, virus_card, target_organ, target_player, owner, game_state):
        medicine = target_organ.remove_medicine()
        game_state.add_card_to_discard_pile(medicine)
        game_state.add_card_to_discard_pile(virus_card)
        target_organ.reset_wild_card()

    def on_medicine_play(self, medicine_card, target_organ, game_state):
        target_organ.add_medicine(medicine_card)


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

    def on_virus_play(self, virus_card, target_organ, target_player, owner, game_state):
        return True

    def on_medicine_play(self, medicine_card, target_organ, game_state):
        return True
