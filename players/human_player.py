from typing import List

from players import BasePlayer
from enums import Action, CardColor


class HumanPlayer(BasePlayer):
    def decide_action(self, game_state):
        print(f"\nYour hand: {self.hand}")
        print(f"Your body: {self.body}")

        while True:
            choice = input("Choose action (Play or Discard): ").lower()
            if choice == 'play':
                return Action.PLAY
            elif choice == 'discard':
                return Action.DISCARD
            else:
                print("Invalid choice.")

    def decide_opponent(self, game_state, card):
        opponents = game_state.get_opponents(self)
        print("\nOpponents:")
        for i, opponent in enumerate(opponents):
            print(f"{i + 1}. {opponent.name} body: {opponent.body}")

        while True:
            try:
                choice = int(input("Choose opponent (enter opponent number): "))
                if 1 <= choice <= len(opponents):
                    return opponents[choice - 1]
                else:
                    print("Invalid choice. Please enter a valid opponent number.")
            except ValueError:
                print("Invalid input. Please enter a number.")


    def decide_organ_color(self, game_state, opponent_body=None):
        print()
        while True:
            try:
                choice = int(input(f"Choose {"opponent's" if opponent_body else 'your'} organ color (1: Red, 2: Yellow, 3: Blue, 4: Green, 5: Wild): "))
                if 1 <= choice <= 5:
                    return list(CardColor)[choice - 1]
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def decide_card_to_play_index(self, game_state) -> int:
        print()
        for i, card in enumerate(self.hand):
            print(f"{i + 1}. {card}")

        while True:
            try:
                choice = int(input("Choose card to play (enter card number): "))
                if 1 <= choice <= len(self.hand):
                    return choice - 1
                else:
                    print("Invalid choice. Please enter a valid card number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def decide_cards_to_discard_indices(self, game_state) -> List[int]:
        print()
        for i, card in enumerate(self.hand):
            print(f"{i + 1}. {card}")
        while True:
            try:
                choices_str = input("Choose cards to discard (enter card numbers separated by commas): ")
                choices = [int(c.strip()) for c in choices_str.split(",")]
                if all(1 <= c <= len(self.hand) for c in choices) and len(choices) <= 3:
                    return [c - 1 for c in choices]
                else:
                    print("Invalid choices. Please enter valid card numbers separated by commas.")
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")
