from abc import ABC, abstractmethod

from enums import TreatmentName, CardType, OrganState, CardColor


class Card(ABC):
    def __init__(self, name: str, card_type: CardType):
        self.name = name
        self.type = card_type

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> CardType:
        return self.type

    @abstractmethod
    def play(self, game: 'VirusGame', owner: 'Player') -> bool:
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

    def play(self, game: 'VirusGame', owner: 'Player') -> bool:
        if self.color == CardColor.WILD:
            target_color = owner.decide_organ_color()
        else:
            target_color = self.color
        print('Target color:', target_color)
        target_organ = next((organ for organ in owner.body if organ.color == target_color), None)
        if not target_organ or target_organ.state == OrganState.IMMUNISED:
            return True
        elif target_organ.state == OrganState.HEALTHY:
            target_organ.add_medicine(self)
            if target_organ.color == CardColor.WILD:
                target_organ.color = self.color
        elif target_organ.state == OrganState.INFECTED:
            virus = target_organ.remove_virus()
            game.add_to_discard_pile(virus)
            game.add_to_discard_pile(self)
            if target_organ.original_color == CardColor.WILD:
                target_organ.color = CardColor.WILD
        elif target_organ.state == OrganState.VACCINATED:
            target_organ.add_medicine(self)
        else:
            raise ValueError("Unknown organ state: %s" % target_organ.state)


class Virus(Card):
    def __init__(self, color):
        self.name = f"{color} {CardType.VIRUS}"
        self.color = color
        super().__init__(self.name, CardType.VIRUS)

    def play(self, game: 'VirusGame', owner: 'Player') -> bool:
        opponents = game.get_opponents(owner)
        target = owner.decide_opponent(opponents)
        if self.color == CardColor.WILD:
            target_color = owner.decide_organ_color()
        else:
            target_color = self.color
        target_organ = next((organ for organ in target.body if organ.color == target_color), None)
        if not target_organ or target_organ.state == OrganState.IMMUNISED:
            return True
        elif target_organ.state == OrganState.HEALTHY:
            target_organ.add_virus(self)
            if target_organ.color == CardColor.WILD:
                target_organ.color = self.color
        elif target_organ.state == OrganState.INFECTED:
            self.discard(game)
        elif target_organ.state == OrganState.VACCINATED:
            medicine = target_organ.remove_medicine()
            game.deck.discard(medicine)
            game.deck.discard(self)
            if target_organ.original_color == CardColor.WILD:
                target_organ.color = CardColor.WILD
        else:
            raise ValueError("Unknown organ state: %s" % target_organ.state)


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
        return f"{self.name} ({'+' * len(self.medicines)}{'-' * len(self.viruses)})"

    def play(self, game: 'VirusGame', owner: 'Player') -> bool:
        if any(organ.color == self.color for organ in owner.body):
            return True
        owner.body.append(self)

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

    def play(self, game: 'VirusGame', owner: 'Player') -> bool:
        if self.name == TreatmentName.TRANSPLANT:
            opponents = game.get_opponents(owner)
            target = owner.decide_opponent(opponents)
            color = owner.decide_organ_color()
            try:
                stolen_organ = next(organ for organ in target.body if organ.color == color)
                given_organ = next(organ for organ in owner.body if organ.color == color)
            except StopIteration:
                return True
            target.body.remove(stolen_organ)
            owner.body.append(stolen_organ)
            owner.body.remove(given_organ)
            target.body.append(given_organ)
        elif self.name == TreatmentName.ORGAN_THIEF:
            opponents = game.get_opponents(owner)
            target = owner.decide_opponent(opponents)
            color = owner.decide_organ_color()
            try:
                stolen_organ = next(organ for organ in target.body if organ.color == color)
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
                    is_error = virus.play(game, owner)
                    if is_error:
                        errors += 1
                    else:
                        owner_organ.remove_virus()
            if errors != 0 and errors == num_viruses:
                return True
        elif self.name == TreatmentName.LATEX_GLOVE:
            opponents = game.get_opponents(owner)
            for opponent in opponents:
                while opponent.hand:
                    card = opponent.hand.pop()
                    card.discard(game)
        elif self.name == TreatmentName.MEDICAL_ERROR:
            opponents = game.get_opponents(owner)
            target = owner.decide_opponent(opponents)
            owner.body, target.body = target.body, owner.body
        else:
            raise ValueError("Unknown treatment name: %s" % self.name)

        self.discard(game)
