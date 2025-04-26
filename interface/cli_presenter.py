from interface.base_presenter import BasePresenter


class CLIPresenter(BasePresenter):
    def print_game_start(self) -> None:
        print("GAME START")

    def print_game_over(self, winner: 'BasePlayer') -> None:
        print("GAME OVER")
        print("Winner:", winner)

    def print_separator(self) -> None:
        print("=" * 50)

    def print_state(self, state_info: dict) -> None:
        print("Current player:", state_info.get('current_player'))
        print("State array:", state_info.get('state_array'))
        for player_state in state_info.get('players', []):
            print(player_state)
        deck = state_info.get('deck', [])
        discard_pile = state_info.get('discard_pile', [])
        print(f"Deck ({len(deck)}):", deck)
        print(f"Discard pile ({len(discard_pile)}):", discard_pile)

    def print_output_array(self, output_arr):
        print('Output array:', output_arr)

    def print_subset_array(self, subset_arr):
        print('Subset array:', subset_arr)
