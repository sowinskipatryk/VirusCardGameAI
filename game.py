from game_config import GameConfig
from enums import OrganState
from players import BasePlayer
from game_state import GameState


class VirusGame:
    def __init__(self, config: GameConfig) -> None:
        if not config.is_valid():
            raise ValueError("The game configuration is invalid!")
        self.state = GameState(config.players)

    def start(self) -> None:
        print('GAME START')
        self.state.print_state()
        winner = None
        while not winner:
            winner = self.play_turn()
            self.state.print_state()
        print('GAME OVER')
        print('Winner:', winner)
        return winner

    @staticmethod
    def check_win_condition(player: BasePlayer) -> bool:
        healthy_organs = [organ for organ in player.body if organ.state != OrganState.INFECTED]
        return len(healthy_organs) >= 4 # check if player has four not infected (healthy/vaccinated/immunised) organs

    def play_turn(self) -> BasePlayer:
        current_player = self.state.get_current_player()
        print('Current player:', current_player)
        if len(current_player.hand) == 3:
            current_player.make_move(self.state)
            if self.check_win_condition(current_player):
                return current_player
        self.state.complete_hand(current_player)
        self.state.next_player()
