import random

from cards import Card, Organ, Virus, Medicine, Treatment
from enums import CardColor, TreatmentName


class Deck:
    def __init__(self):
        self.cards: list[Card] = []
        self.discard_pile: list[Card] = []
        self._create_cards()
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw_card(self) -> Card:
        if not self.cards:
            self.cards = self.discard_pile[::-1]
            self.discard_pile = []
        card = self.cards.pop()
        print('drawing', card)
        return card

    def discard(self, card: Card) -> None:
        print('discarding', card)
        self.discard_pile.append(card)

    def _create_cards(self) -> None:
        self.cards += [Organ(CardColor.WILD)]
        self.cards += [Organ(CardColor.RED) for _ in range(5)]
        self.cards += [Organ(CardColor.GREEN) for _ in range(5)]
        self.cards += [Organ(CardColor.BLUE) for _ in range(5)]
        self.cards += [Organ(CardColor.YELLOW) for _ in range(5)]
        self.cards += [Virus(CardColor.WILD)]
        self.cards += [Virus(CardColor.RED) for _ in range(4)]
        self.cards += [Virus(CardColor.GREEN) for _ in range(4)]
        self.cards += [Virus(CardColor.BLUE) for _ in range(4)]
        self.cards += [Virus(CardColor.YELLOW) for _ in range(4)]
        self.cards += [Medicine(CardColor.WILD) for _ in range(4)]
        self.cards += [Medicine(CardColor.RED) for _ in range(4)]
        self.cards += [Medicine(CardColor.GREEN) for _ in range(4)]
        self.cards += [Medicine(CardColor.BLUE) for _ in range(4)]
        self.cards += [Medicine(CardColor.YELLOW) for _ in range(4)]
        self.cards += [Treatment(TreatmentName.CONTAGION) for _ in range(2)]
        self.cards += [Treatment(TreatmentName.ORGAN_THIEF) for _ in range(3)]
        self.cards += [Treatment(TreatmentName.TRANSPLANT) for _ in range(3)]
        self.cards += [Treatment(TreatmentName.LATEX_GLOVE) for _ in range(1)]
        self.cards += [Treatment(TreatmentName.MEDICAL_ERROR) for _ in range(1)]
