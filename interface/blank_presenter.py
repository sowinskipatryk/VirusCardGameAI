from interface.base_presenter import BasePresenter


class BlankPresenter(BasePresenter):
    def print_game_start(self) -> None:
        pass

    def print_game_over(self, winner: 'BasePlayer') -> None:
        pass

    def print_separator(self) -> None:
        pass

    def print_state(self, state_info: dict) -> None:
        pass

    def print_output_array(self, output_arr):
        pass

    def print_subset_array(self, subset_arr):
        pass

    def print_card_play_status_success(self):
        pass

    def print_card_play_status_fail(self):
        pass

    def print_decision(self, decision):
        pass

    def print_card(self, card):
        pass
