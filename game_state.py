import random
from collections import defaultdict

from deck import Deck
from enums import CardColor, TreatmentName, CardType


class GameState:
    def __init__(self, players):
        self.players = players
        self.num_players = len(players)
        self.deck = Deck()
        self.current_player_index = random.randint(0, self.num_players - 1)
        self.move_history = []

    def get_current_player(self):
        return self.players[self.current_player_index]

    def get_player_by_index(self, index):
        return self.players[index]

    def next_player(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % self.num_players

    def get_opponents(self, current_player):
        opponents = [player for player in self.players if player != current_player]
        return opponents

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
        current_player = self.get_current_player()
        opponents = self.get_opponents(current_player)
        card_colors = list(CardColor)
        treatments = list(TreatmentName)
        color_card_types = [CardType.ORGAN, CardType.MEDICINE, CardType.VIRUS]

        player_organ_state_index = 0
        opponent_organ_state_index = player_organ_state_index + len(card_colors)
        player_treatments_index = opponent_organ_state_index + len(opponents) * len(card_colors)
        player_color_hand_cards_index = player_treatments_index + len(treatments)

        state_array = [0] * (len(card_colors) * self.num_players + len(treatments) + len(color_card_types) * len(card_colors))

        for organ in current_player.body:
            state_array[player_organ_state_index + card_colors.index(organ.color)] = organ.state.value

        for i, opponent in enumerate(opponents):
            for organ in opponent.body:
                state_array[opponent_organ_state_index + (len(card_colors) * i) + card_colors.index(organ.color)] = organ.state.value

        for card in current_player.hand:
            if card.name in treatments:
                state_array[player_treatments_index + treatments.index(card.name)] += 1
            else:
                state_array[player_color_hand_cards_index + color_card_types.index(card.type) * len(card_colors) + card_colors.index(card.color)] += 1

        state_array.append(len(self.deck.cards))
        state_array.append(len(self.deck.discard_pile))
        return state_array

    def add_card_to_discard_pile(self, card):
        self.deck.discard(card)
