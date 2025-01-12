import random
from collections import defaultdict

from deck import Deck
from game_config import GameConfig
from enums import OrganState
from players import BasePlayer


class VirusGame:
    def __init__(self, config: GameConfig):
        if not config.is_valid():
            raise ValueError("The game configuration is invalid!")
        self.players = config.players
        self.num_players = len(self.players)
        self.deck = Deck()
        self.current_player_index = random.randint(0, self.num_players - 1)
        self.state = defaultdict()

    def start(self) -> None:
        print('GAME START')
        self.print_state()
        winner = None
        while not winner:
            winner = self.play_turn()
            self.print_state()
        print('GAME OVER')
        print('Winner:', winner)
        return winner

    @staticmethod
    def check_win_condition(player: BasePlayer) -> bool:
        healthy_organs = [organ for organ in player.body if organ.state != OrganState.INFECTED]
        return len(healthy_organs) >= 4

    def play_turn(self) -> BasePlayer:
        current_player = self.players[self.current_player_index]
        print('Current player:', current_player)
        if len(current_player.hand) == 3:
            is_error = current_player.make_move(self)
            if self.check_win_condition(current_player):
                return current_player
        self.complete_hand(current_player)
        self.next_player()

    def next_player(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % self.num_players

    def complete_hand(self, player: BasePlayer) -> None:
        amount = 3 - len(player.hand)
        for _ in range(amount):
            drawn_card = self.deck.draw_card()
            player.hand.append(drawn_card)

    def get_opponents(self, player: BasePlayer):
        opponents = [opponent for opponent in self.players if opponent != player]
        return opponents

    def get_state(self):
        state = defaultdict()
        state['players'] = []
        for player in self.players:
            state['players'].append({
                'name': player.name,
                'hand': player.hand,
                'body': player.body,
                'cards_used': player.cards_used,
                'cards_tried': player.cards_tried,
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
