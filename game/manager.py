from game.players import PlayerFactory
from game.enums import OrganState
from game.players import BasePlayer
from game.constants import GameConstants
from game.state import GameState
from game.interface import presenter


class GameManager:
    def __init__(self, player_factory: PlayerFactory) -> None:
        if not player_factory.is_valid():
            raise ValueError("The game configuration is invalid!")
        self.config = player_factory
        self.state = GameState(player_factory.players)

    def run(self) -> BasePlayer:
        presenter.print_game_start()
        winner = None
        turn_counter = 0
        max_turns = 10_000
        while not winner:
            winner = self.play_turn()
            turn_counter += 1
            if turn_counter > max_turns:
                raise RuntimeError(f"Game did not finish after {max_turns} turns")
        self.state.set_game_over()
        presenter.print_game_over(winner)
        return winner

    def check_win_condition(self) -> bool:
        healthy_organs = [organ for organ in self.state.current_player.body if organ.state != OrganState.INFECTED]
        return len(healthy_organs) >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN  # check if player has X healthy (or vaccinated or immunised) organs

    def play_turn(self) -> BasePlayer:
        presenter.print_separator()
        presenter.print_state(self._compose_state_info(self.state.current_player))

        if self.state.current_player.hand:  # if latex glove card was played - skip first phase and complete hand right away
            self.state.current_player.take_turn(self.state)

        self.state.complete_hand(self.state.current_player)

        if self.check_win_condition():
            self.game_over = True
            self.winner = self.state.current_player
            return self.winner

        winner = self.state.get_winner()
        if winner:
            presenter.print_state(self._compose_state_info(self.state.current_player))
            return winner

        self.state.next_player()

    def _compose_state_info(self, current_player: BasePlayer) -> dict:
        state_info = self.state.get_state_info()
        state_info['current_player'] = current_player
        state_info['state_array'] = self.state.get_state_array_for_ai()
        return state_info
