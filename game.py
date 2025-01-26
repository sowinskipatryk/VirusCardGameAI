from game_config import GameConfig
from enums import OrganState
from players import BasePlayer
from game_state import GameState

# handles the logic of the game, including determining when the game ends and who wins
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
        self.print_state()
        if current_player.hand: # if latex glove card was played - skip first phase and complete hand right away
            current_player.take_turn(self.state)
            if self.check_win_condition(current_player):
                self.print_state()
                return current_player
        self.state.complete_hand(current_player)
        self.state.next_player()

    def print_state(self):
        state = self.state.get_state_info()
        print('Current player:', self.state.get_current_player())
        print('State array:', self.state.get_state_array_for_ai())
        for player_state in state['players']:
            print(player_state)
        print(len(state['deck']), state['deck'])
        print(len(state['discard_pile']), state['discard_pile'])
