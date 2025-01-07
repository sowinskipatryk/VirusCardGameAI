import random

from cards import Card, Organ, Virus, Medicine, Transplant, OrganThief, Contagion, LatexGlove, MedicalError
from enums import CardColor


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
        return self.cards.pop()

    def discard_card(self, card: Card) -> None:
        self.discard_pile.append(card)

    def _create_cards(self) -> None:
        self.cards += [Organ(CardColor.MULTICOLORED)]
        self.cards += [Organ(CardColor.RED) for _ in range(5)]
        self.cards += [Organ(CardColor.GREEN) for _ in range(5)]
        self.cards += [Organ(CardColor.BLUE) for _ in range(5)]
        self.cards += [Organ(CardColor.YELLOW) for _ in range(5)]
        self.cards += [Virus(CardColor.MULTICOLORED)]
        self.cards += [Virus(CardColor.RED) for _ in range(4)]
        self.cards += [Virus(CardColor.GREEN) for _ in range(4)]
        self.cards += [Virus(CardColor.BLUE) for _ in range(4)]
        self.cards += [Virus(CardColor.YELLOW) for _ in range(4)]
        self.cards += [Medicine(CardColor.MULTICOLORED)]
        self.cards += [Medicine(CardColor.RED) for _ in range(4)]
        self.cards += [Medicine(CardColor.GREEN) for _ in range(4)]
        self.cards += [Medicine(CardColor.BLUE) for _ in range(4)]
        self.cards += [Medicine(CardColor.YELLOW) for _ in range(4)]
        self.cards += [Contagion() for _ in range(2)]
        self.cards += [OrganThief() for _ in range(3)]
        self.cards += [Transplant() for _ in range(3)]
        self.cards += [LatexGlove() for _ in range(1)]
        self.cards += [MedicalError() for _ in range(1)]
