from abc import ABC, abstractmethod

from enums import TreatmentName, CardType, OrganState, CardColor


class Card(ABC):
    def __init__(self, name: str, card_type: CardType):
        self.name = str(name)
        self.type = card_type

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> CardType:
        return self.type

    @abstractmethod
    def play(self, game_state: 'GameState', owner: 'Player') -> bool:
        pass

    @abstractmethod
    def can_be_played(self, game_state: 'GameState', owner: 'Player') -> bool:
        pass

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def discard(self, game):
        game.add_to_discard_pile(self)


class Medicine(Card):
    def __init__(self, color):
        self.name = f"{color} {CardType.MEDICINE}"
        self.color = color
        super().__init__(self.name, CardType.MEDICINE)

    def play(self, game_state: 'GameState', owner: 'Player') -> bool:
        if self.color == CardColor.WILD:
            target_color = owner.decide_organ_color(game_state, context='wild_medicine')
        else:
            target_color = self.color
        print('Target color:', target_color)
        target_organ = next((organ for organ in owner.body if organ.color in [target_color, CardColor.WILD]), None)
        if not target_organ or target_organ.state == OrganState.IMMUNISED:
            return True
        elif target_organ.state == OrganState.HEALTHY:
            target_organ.add_medicine(self) # Add the medicine to the organ
            if target_organ.color == CardColor.WILD:
                target_organ.color = self.color # Set the medicine color to wild card
        elif target_organ.state == OrganState.INFECTED:
            virus = target_organ.remove_virus() # Remove the virus from the organ
            game_state.add_to_discard_pile(virus) # Discard the virus
            game_state.add_to_discard_pile(self) # Discard the medicine
            if target_organ.original_color == CardColor.WILD:
                target_organ.color = CardColor.WILD # Reset the wild card color
        elif target_organ.state == OrganState.VACCINATED:
            target_organ.add_medicine(self) # Add the medicine to the organ
        else:
            raise ValueError("Unknown organ state: %s" % target_organ.state)

    def can_be_played(self, game_state: 'GameState', owner: 'Player'):
        for organ in owner.body:
            if organ.state != OrganState.IMMUNISED and (self.color == organ.color or self.color == CardColor.WILD):
                return True


class Virus(Card):
    def __init__(self, color):
        self.name = f"{color} {CardType.VIRUS}"
        self.color = color
        super().__init__(self.name, CardType.VIRUS)

    def play(self, game_state: 'GameState', owner: 'Player') -> bool:
        target = owner.decide_opponent(game_state, self)
        if self.color == CardColor.WILD:
            target_color = owner.decide_organ_color(game_state, target.body)
        else:
            target_color = self.color
        target_organ = next((organ for organ in target.body if organ.color in [target_color, CardColor.WILD]), None)
        if not target_organ or target_organ.state == OrganState.IMMUNISED:
            return True
        elif target_organ.state == OrganState.HEALTHY:
            target_organ.add_virus(self) # Add the virus to the organ
            if target_organ.color == CardColor.WILD:
                target_organ.color = self.color # Assign the virus color to wild card
        elif target_organ.state == OrganState.INFECTED:
            target.body.remove(target_organ) # Remove the twice infected organ from the target body
            target_organ.discard(game_state) # Discard the target organ with one assigned previously virus
            self.discard(game_state) # Discard the currently used virus
        elif target_organ.state == OrganState.VACCINATED:
            medicine = target_organ.remove_medicine() # Remove the medicine from the target organ
            game_state.deck.discard(medicine) # Discard the medicine
            game_state.deck.discard(self) # Discard the virus
            if target_organ.original_color == CardColor.WILD:
                target_organ.color = CardColor.WILD # Reset the wild card color
        else:
            raise ValueError("Unknown organ state: %s" % target_organ.state)

    def can_be_played(self, game_state: 'GameState', owner: 'Player'):
        opponents = game_state.get_opponents(owner)
        for opponent in opponents:
            if any(organ.color in [self.color, CardColor.WILD] and organ.state != OrganState.IMMUNISED for organ in opponent.body):
                return True


class Organ(Card):
    def __init__(self, color):
        self.name = f"{color} {CardType.ORGAN}"
        self.original_color = color
        self.color = color
        self.state = OrganState.HEALTHY
        self.viruses = []
        self.medicines = []
        super().__init__(self.name, CardType.ORGAN)

    def __repr__(self):
        return f"{self.name}{' ('+self.color.upper()+')' if self.color != self.original_color else ''} ({'+' * len(self.medicines)}{'-' * len(self.viruses)})"

    def play(self, game_state: 'GameState', owner: 'Player') -> bool:
        if any(organ.color == self.color for organ in owner.body):
            return True
        owner.body.append(self)

    def can_be_played(self, game_state: 'GameState', owner: 'Player'):
        organ_colors = [organ.color for organ in owner.body]
        if self.color not in organ_colors:
            return True

    def discard(self, game):
        self.state = OrganState.HEALTHY
        super().discard(game)
        while self.viruses:
            virus = self.remove_virus()
            game.add_to_discard_pile(virus)
        while self.medicines:
            medicine = self.remove_medicine()
            game.add_to_discard_pile(medicine)

    def add_virus(self, virus_card):
        self.viruses.append(virus_card)
        self.resolve_state()

    def remove_virus(self):
        virus = self.viruses.pop()
        self.resolve_state()
        return virus

    def add_medicine(self, medicine_card):
        self.medicines.append(medicine_card)
        self.resolve_state()

    def remove_medicine(self):
        medicine = self.medicines.pop()
        self.resolve_state()
        return medicine

    def resolve_state(self):
        if not self.viruses and not self.medicines:
            self.state = OrganState.HEALTHY
        elif self.viruses and not self.medicines:
            self.state = OrganState.INFECTED
        elif not self.viruses and len(self.medicines) == 1:
            self.state = OrganState.VACCINATED
        elif not self.viruses and len(self.medicines) == 2:
            self.state = OrganState.IMMUNISED
        else:
            raise ValueError(f"Invalid organ state: {'+' * len(self.medicines)}{'-' * len(self.viruses)}")

class Treatment(Card):
    def __init__(self, name):
        super().__init__(name, CardType.TREATMENT)

    def play(self, game_state: 'GameState', owner: 'Player') -> bool:
        if self.name == TreatmentName.TRANSPLANT:
            target = owner.decide_opponent(game_state, self)
            given_color = owner.decide_organ_color(game_state)
            stolen_color = owner.decide_organ_color(game_state, target.body)
            try:
                stolen_organ = next(organ for organ in target.body if organ.color == stolen_color)
                given_organ = next(organ for organ in owner.body if organ.color == given_color)
            except StopIteration:
                return True
            target.body.remove(stolen_organ)
            owner.body.append(stolen_organ)
            owner.body.remove(given_organ)
            target.body.append(given_organ)
        elif self.name == TreatmentName.ORGAN_THIEF:
            target = owner.decide_opponent(game_state, self)
            target_color = owner.decide_organ_color(game_state, target.body)
            try:
                stolen_organ = next(organ for organ in target.body if organ.color == target_color and organ.color not in [organ.color for organ in owner.body])
            except StopIteration:
                return True
            target.body.remove(stolen_organ)
            owner.body.append(stolen_organ)
        elif self.name == TreatmentName.CONTAGION:
            infected_organs = [organ for organ in owner.body if organ.state == OrganState.INFECTED]
            num_viruses = 0
            errors = 0
            for owner_organ in infected_organs:
                for virus in owner_organ.viruses:
                    num_viruses += 1
                    is_error = virus.play(game_state, owner)
                    if is_error:
                        errors += 1
                    else:
                        owner_organ.remove_virus()
            if errors != 0 and errors == num_viruses:
                return True
        elif self.name == TreatmentName.LATEX_GLOVE:
            opponents = game_state.get_opponents(owner)
            for opponent in opponents:
                while opponent.hand:
                    card = opponent.hand.pop()
                    card.discard(game_state)
        elif self.name == TreatmentName.MEDICAL_ERROR:
            target = owner.decide_opponent(game_state, self)
            owner.body, target.body = target.body, owner.body
        else:
            raise ValueError("Unknown treatment name: %s" % self.name)

        self.discard(game_state)

    def can_be_played(self, game_state: 'GameState', owner: 'Player'):
        if self.name == TreatmentName.ORGAN_THIEF:
            opponents = game_state.get_opponents(owner)
            for opponent in opponents:
                owner_organ_colors = [organ.color for organ in owner.body]
                if any(organ.color not in owner_organ_colors for organ in opponent.body):
                    return True

        if self.name == TreatmentName.CONTAGION:
            infected_organs = [organ for organ in owner.body if organ.state == OrganState.INFECTED]
            for organ in infected_organs:
                for virus in organ.viruses:
                    if virus.can_be_played(game_state, owner):
                        return True

        if self.name == TreatmentName.LATEX_GLOVE:
            return True

        if self.name == TreatmentName.MEDICAL_ERROR:
            opponents = game_state.get_opponents(owner)
            if any(opponent.body for opponent in opponents):
                return True

        if self.name == TreatmentName.TRANSPLANT:
            if not any(organ for organ in owner.body if organ.state != OrganState.IMMUNISED):
                return False

            opponents = game_state.get_opponents(owner)
            for opponent in opponents:
                if any(organ for organ in opponent.body if organ.state != OrganState.IMMUNISED):
                    return True
