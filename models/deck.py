import random

from game.game_constants import GameConstants
from models.cards import Card, Organ, Virus, Medicine, MedicalError, Contagion, LatexGlove, OrganThief, Transplant
from enums import CardColor


class Deck:
    def __init__(self):
        self.cards: list[Card] = []
        self.discard_pile: list[Card] = []
        self._create_cards()
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def refill_deck(self):
        self.cards = self.discard_pile[::-1]
        self.discard_pile = []

    def draw_card(self) -> Card:
        if not self.cards:
            self.refill_deck()
        card = self.cards.pop()
        # print('drawing', card)
        return card

    def discard(self, card: Card) -> None:
        # print('discarding', card)
        self.discard_pile.append(card)

    def _create_cards(self) -> None:
        self.cards += [Organ(CardColor.WILD) for _ in range(GameConstants.NUM_WILD_ORGANS)]
        self.cards += [Organ(CardColor.RED) for _ in range(GameConstants.NUM_COLORED_ORGANS)]
        self.cards += [Organ(CardColor.GREEN) for _ in range(GameConstants.NUM_COLORED_ORGANS)]
        self.cards += [Organ(CardColor.BLUE) for _ in range(GameConstants.NUM_COLORED_ORGANS)]
        self.cards += [Organ(CardColor.YELLOW) for _ in range(GameConstants.NUM_COLORED_ORGANS)]
        self.cards += [Virus(CardColor.WILD) for _ in range(GameConstants.NUM_WILD_VIRUSES)]
        self.cards += [Virus(CardColor.RED) for _ in range(GameConstants.NUM_COLORED_VIRUSES)]
        self.cards += [Virus(CardColor.GREEN) for _ in range(GameConstants.NUM_COLORED_VIRUSES)]
        self.cards += [Virus(CardColor.BLUE) for _ in range(GameConstants.NUM_COLORED_VIRUSES)]
        self.cards += [Virus(CardColor.YELLOW) for _ in range(GameConstants.NUM_COLORED_VIRUSES)]
        self.cards += [Medicine(CardColor.WILD) for _ in range(GameConstants.NUM_WILD_MEDICINES)]
        self.cards += [Medicine(CardColor.RED) for _ in range(GameConstants.NUM_COLORED_MEDICINES)]
        self.cards += [Medicine(CardColor.GREEN) for _ in range(GameConstants.NUM_COLORED_MEDICINES)]
        self.cards += [Medicine(CardColor.BLUE) for _ in range(GameConstants.NUM_COLORED_MEDICINES)]
        self.cards += [Medicine(CardColor.YELLOW) for _ in range(GameConstants.NUM_COLORED_MEDICINES)]
        self.cards += [Contagion() for _ in range(GameConstants.NUM_CONTAGIONS)]
        self.cards += [OrganThief() for _ in range(GameConstants.NUM_ORGAN_THIEVES)]
        self.cards += [Transplant() for _ in range(GameConstants.NUM_TRANSPLANTS)]
        self.cards += [LatexGlove() for _ in range(GameConstants.NUM_LATEX_GLOVES)]
        self.cards += [MedicalError() for _ in range(GameConstants.NUM_MEDICAL_ERRORS)]
