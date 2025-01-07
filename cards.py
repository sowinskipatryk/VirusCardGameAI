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
    def play(self, game: 'VirusGame', owner: 'Player') -> None:
        pass

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"

    def __repr__(self) -> str:
        return self.name

    def discard(self, game):
        game.deck.discard(self)


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
        target_organ = next((organ for organ in owner.body if organ.color == target_color), None)
        if not target_organ or target_organ.state == OrganState.IMMUNISED:
            return True
        elif target_organ.state == OrganState.HEALTHY:
            target_organ.medicines.append(self)
            target_organ.state = OrganState.VACCINATED
            if target_organ.color == CardColor.WILD:
                target_organ.color = self.color
        elif target_organ.state == OrganState.INFECTED:
            virus_card = target_organ.viruses.pop()
            game.deck.discard(virus_card)
            game.deck.discard(self)
            target_organ.state = OrganState.HEALTHY
            if target_organ.original_color == CardColor.WILD:
                target_organ.color = CardColor.WILD
        elif target_organ.state == OrganState.VACCINATED:
            target_organ.medicines.append(self)
            target_organ.state = OrganState.IMMUNISED
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
            target_organ.viruses.append(self)
            target_organ.state = OrganState.INFECTED
            if target_organ.color == CardColor.WILD:
                target_organ.color = self.color
        elif target_organ.state == OrganState.INFECTED:
            self.discard(game)
        elif target_organ.state == OrganState.VACCINATED:
            medicine_card = target_organ.medicines.pop()
            game.deck.discard(medicine_card)
            game.deck.discard(self)
            target_organ.state = OrganState.HEALTHY
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

    def play(self, game: 'VirusGame', owner: 'Player') -> bool:
        if any(organ.color == self.color for organ in owner.body):
            return True
        owner.body.append(self)

    def discard(self, game):
        self.state = OrganState.HEALTHY
        super().discard(game)
        while self.viruses:
            game.discard(self.viruses.pop())
        while self.medicines:
            game.discard(self.medicines.pop())

    def add_virus(self, virus_card):
        self.viruses.append(virus_card)

    def add_medicine(self, medicine_card):
        self.medicines.append(medicine_card)

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
            for organ in infected_organs:
                for virus in organ.viruses:
                    opponents = game.get_opponents(owner)
                    target = owner.decide_opponent(opponents)
                    try:
                        target_organ = next(organ for organ in target.body if organ.color == virus.color)
                        target_organ.add_virus(virus)
                        organ.viruses.remove(virus)
                        if not organ.viruses:
                            organ.state = OrganState.HEALTHY
                    except StopIteration:
                        pass
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
