from abc import ABC, abstractmethod


class BasePresenter(ABC):
    @abstractmethod
    def print_game_start(self) -> None:
        pass

    @abstractmethod
    def print_game_over(self, winner: 'BasePlayer') -> None:
        pass

    @abstractmethod
    def print_separator(self) -> None:
        pass

    @abstractmethod
    def print_state(self, state_info: dict) -> None:
        pass

    @abstractmethod
    def print_output_array(self, output_arr):
        pass

    @abstractmethod
    def print_subset_array(self, subset_arr):
        pass

    @abstractmethod
    def print_card_play_status_success(self):
        pass

    @abstractmethod
    def print_card_play_status_fail(self):
        pass

    @abstractmethod
    def print_decision(self, decision):
        pass

    @abstractmethod
    def print_card(self, card):
        pass
