from game_config import GameConfig
from enums import OrganState
from players import BasePlayer
from game_state import GameState


class VirusGame:
    def __init__(self, config: GameConfig) -> None:
        if not config.is_valid():
            raise ValueError("The game configuration is invalid!")
        self.state = GameState(config.players)

    def run(self) -> BasePlayer:
        print('GAME START')
        winner = None
        while not winner:
            winner = self.play_turn()
        print('GAME OVER')
        print('Winner:', winner)
        return winner

    @staticmethod
    def check_win_condition(player: BasePlayer) -> bool:
        healthy_organs = [organ for organ in player.body if organ.state != OrganState.INFECTED]
        return len(healthy_organs) >= GameConfig.num_organs_to_win # check if player has X healthy(/vaccinated/immunised) organs

    def play_turn(self) -> BasePlayer:
        current_player = self.state.get_current_player()
        self.state.print_state()
        if current_player.hand: # if latex glove card was played - skip first phase and complete hand right away
            current_player.make_move(self.state)
            if self.check_win_condition(current_player):
                self.state.print_state()
                return current_player
        self.state.complete_hand(current_player)
        self.state.next_player()
