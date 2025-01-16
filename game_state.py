import random
from collections import defaultdict

from deck import Deck


class GameState:
    def __init__(self, players):
        self.players = players
        self.num_players = len(players)
        self.deck = Deck()
        self.current_player_index = random.randint(0, self.num_players - 1)
        self.move_history = []

    def get_current_player(self):
        return self.players[self.current_player_index]

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

    def get_state(self):
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

    def print_state(self):
        state = self.get_state()
        for player_state in state['players']:
            print(player_state)
        print(len(state['deck']), state['deck'])
        print(len(state['discard_pile']), state['discard_pile'])

    def add_to_discard_pile(self, card):
        self.deck.discard(card)
