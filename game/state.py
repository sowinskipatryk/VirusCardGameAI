import copy
import random
from collections import defaultdict

from game.constants import GameConstants
from game.models.deck import Deck
from game.enums import CardColor, TreatmentName, CardType, OrganState


class GameState:
    def __init__(self, players):
        self.players = players
        self.num_players = len(players)
        self.deck = Deck()
        self.current_player_index = random.randint(0, self.num_players - 1)
        self.move_history = []
        self.game_over = False
        self.winner = None

    def get_winner(self):
        return self.winner

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def get_current_player(self):
        return self.players[self.current_player_index]

    def get_player_index(self, player):
        return self.players.index(player)

    def get_player_by_index(self, index):
        return self.players[index]

    def get_player_by_name(self, name: str):
        for player in self.players:
            if player.name == name:
                return player
        return next((player for player in self.players if player.name == name), None)

    def next_player(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % self.num_players

    def get_opponents(self, current_player):
        opponents = [player for player in self.players if player != current_player]
        return opponents

    def check_win_condition(self, player: 'BasePlayer') -> bool:
        healthy_organs = [organ for organ in player.body if organ.state != OrganState.INFECTED]
        return len(healthy_organs) >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN  # check if player has X healthy (or vaccinated or immunised) organs

    def complete_hand(self, player: 'BasePlayer') -> None:
        amount = 3 - len(player.hand)
        for _ in range(amount):
            drawn_card = self.deck.draw_card()
            player.hand.append(drawn_card)

    def get_state_info(self):
        state = defaultdict()
        state['players'] = []
        for player in self.players:
            state['players'].append({
                'name': player.name,
                'hand': player.hand,
                'body': player.body,
                'move_history': player.move_history,
            })
        state['deck'] = self.deck.cards
        state['discard_pile'] = self.deck.discard_pile
        return state

    def get_state_array_for_ai(self):
        card_colors = list(CardColor)
        treatments = list(TreatmentName)
        organ_states = list(OrganState)
        color_card_types = [CardType.ORGAN, CardType.MEDICINE, CardType.VIRUS]

        BODY_INDEX = 0
        PLAYER_INDEX = BODY_INDEX + (len(self.players) * len(OrganState) * len(CardColor))
        COLOR_CARDS_INDEX = PLAYER_INDEX + len(self.players)
        TREATMENTS_INDEX = COLOR_CARDS_INDEX + (len(CardColor) * len(color_card_types))
        DECK_INDEX = TREATMENTS_INDEX + len(TreatmentName)
        DISCARD_PILE_INDEX = DECK_INDEX + 1
        num_inputs = DISCARD_PILE_INDEX + 1

        state_array = [0.] * num_inputs
        for player_id, player in enumerate(self.players):
            for organ in player.body:
                state_array[BODY_INDEX + (player_id * len(OrganState) * len(CardColor)) + (organ_states.index(organ.state) * len(CardColor)) + card_colors.index(organ.color)] = 1.

        current_player_id = self.get_player_index(self.current_player)
        state_array[PLAYER_INDEX + current_player_id] = 1.

        for card in self.current_player.hand:
            if card.name in treatments:
                state_array[TREATMENTS_INDEX + treatments.index(card.name)] = 1.
            elif card.type in color_card_types:
                state_array[COLOR_CARDS_INDEX + (color_card_types.index(card.type) * len(CardColor)) + card_colors.index(card.color)] = 1.
            else:
                raise ValueError

        state_array[DECK_INDEX] = len(self.deck.cards) / GameConstants.NUM_TOTAL_CARDS
        state_array[DISCARD_PILE_INDEX] = len(self.deck.discard_pile) / GameConstants.NUM_TOTAL_CARDS
        return state_array

    def add_card_to_discard_pile(self, card):
        self.deck.discard(card)

    def clone(self):
        return copy.deepcopy(self)

    def is_game_over(self):
        return self.game_over

    def set_game_over(self):
        self.game_over = True
