import neat
import pickle

import os
from typing import List

from players import BasePlayer
from enums import Action, CardColor
from game.game_state import GameState
from interface import presenter


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

neat_config_path = os.path.join(CURRENT_DIR, 'training', 'neat-config.txt')
best_genome_path = os.path.join(CURRENT_DIR, 'training', 'best_genome.pkl')

neat_config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                          neat.DefaultSpeciesSet, neat.DefaultStagnation,
                          neat_config_path)


def get_best_genome():
    with open(best_genome_path, "rb") as f:
        return pickle.load(f)


class NEATPlayer(BasePlayer):
    def __init__(self, name: str, genome=None, config=neat_config):
        super().__init__(name)
        self.genome = get_best_genome() if genome is None else genome
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, config)

        self.action_index = 0
        self.card_index = self.action_index + 2
        self.discard_count_index = self.card_index + 3
        self.discard_index = self.discard_count_index + 3
        self.color_index = self.discard_index + 3
        self.opponent_index = self.color_index + len(CardColor)

        self.score = 0

    def decide_action(self, game_state: GameState) -> Action:
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        subset_arr = output_arr[self.action_index: self.action_index + 2]
        presenter.print_subset_array(subset_arr)
        actions = list(Action)
        action_index = subset_arr.index(max(subset_arr))
        return actions[action_index]

    def decide_card_to_play_index(self, game_state: GameState) -> int:
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        subset_arr = output_arr[self.card_index: self.card_index + 3]
        card_index = subset_arr.index(max(subset_arr))
        return card_index

    def decide_cards_to_discard_indices(self, game_state: GameState) -> List[int]:
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        subset_arr = output_arr[self.discard_count_index: self.discard_count_index + 3]
        presenter.print_subset_array(subset_arr)
        discard_count = subset_arr.index(max(subset_arr)) + 1

        subset_arr = output_arr[self.discard_index: self.discard_index + 3]
        presenter.print_subset_array(subset_arr)
        discard_indices = sorted(range(len(subset_arr)), key=lambda i: subset_arr[i], reverse=True)[:discard_count]
        return discard_indices

    def decide_opponent(self, game_state: GameState, card) -> BasePlayer:
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        opponents = game_state.get_opponents(self)

        subset_arr = output_arr[self.opponent_index: self.opponent_index + len(opponents)]
        presenter.print_subset_array(subset_arr)

        opponent_index = subset_arr.index(max(subset_arr))
        return opponents[opponent_index]

    def decide_organ_color(self, game_state: GameState, opponent_body=None) -> CardColor:
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        subset_arr = output_arr[self.color_index: self.color_index + len(CardColor)]
        color_index = subset_arr.index(max(subset_arr))
        colors = list(CardColor)
        return colors[color_index]

    def get_score(self):
        return self.score

    def get_final_score(self):
        score = self.score
        score -= (10 * self.num_failed_moves)
        score += (10 * self.num_successful_moves)
        score += (20 * len(self.body))
        score += (40 * self.get_immunised_organs_num())
        score += (10 * self.get_vaccinated_organs_num())
        score -= (10 * self.get_infected_organs_num())
        return score

    def add_card_to_body(self, organ: 'Organ') -> None:
        super().add_card_to_body(organ)
        self.score += 10

    def remove_organ_from_body(self, organ):
        super().remove_organ_from_body(organ)
        self.score -= 10

    def discard_cards(self, game_state, card_ids):
        super().discard_cards(game_state, card_ids)
        self.score -= 10
