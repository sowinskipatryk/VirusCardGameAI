from players import PlayerFactory
from enums import OrganState
from players import BasePlayer
from game.game_constants import GameConstants
from game.game_state import GameState
from interface import BlankPresenter


class GameManager:
    def __init__(self, player_factory: PlayerFactory) -> None:
        if not player_factory.is_valid():
            raise ValueError("The game configuration is invalid!")
        self.config = player_factory
        self.state = GameState(player_factory.players)
        self.presenter = BlankPresenter()

    def run(self) -> BasePlayer:
        # self.presenter.print_game_start()
        winner = None
        turn_counter = 0
        max_turns = 10_000
        while not winner:
            winner = self.play_turn()
            turn_counter += 1
            if turn_counter > max_turns:
                raise RuntimeError(f"Game did not finish after {max_turns} turns")
        self.presenter.print_game_over(winner)
        return winner

    def check_win_condition(self, player: BasePlayer) -> bool:
        healthy_organs = [organ for organ in player.body if organ.state != OrganState.INFECTED]
        return len(healthy_organs) >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN  # check if player has X healthy (or vaccinated or immunised) organs

    def play_turn(self) -> BasePlayer:
        self.presenter.print_separator()
        current_player = self.state.get_current_player()
        self.presenter.print_state(self._compose_state_info(current_player))

        if current_player.hand:  # if latex glove card was played - skip first phase and complete hand right away
            current_player.take_turn(self.state)
            if self.check_win_condition(current_player):
                self.presenter.print_state(self._compose_state_info(current_player))
                return current_player

        self.state.complete_hand(current_player)
        self.state.next_player()

    def _compose_state_info(self, current_player: BasePlayer) -> dict:
        state_info = self.state.get_state_info()
        state_info['current_player'] = current_player
        state_info['state_array'] = self.state.get_state_array_for_ai()
        return state_info
