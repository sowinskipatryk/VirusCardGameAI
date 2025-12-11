import neat
import pickle

import os
from typing import List

from game.players import BasePlayer
from game.enums import Action, CardColor
from game.state import GameState
from game.constants import GameConstants
from game.interface import presenter


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
    MAX_OPPONENTS = GameConstants.MAX_PLAYERS - 1  # 5
    
    def __init__(self, name: str, genome=None, config=neat_config):
        super().__init__(name)
        self.genome = get_best_genome() if genome is None else genome
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, config)

        # output indices
        self.action_index = 0
        self.card_index = self.action_index + 2
        self.discard_count_index = self.card_index + 3
        self.discard_index = self.discard_count_index + 3
        self.color_index = self.discard_index + 3
        self.opponent_index = self.color_index + len(CardColor)

        self.score = 0

    def decide_action(self, game_state: GameState) -> Action:
        # check if any card can be played - if not, must discard
        playable = [c for c in self.hand if c.can_be_played(game_state, self)]
        if not playable:
            return Action.DISCARD
        
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        subset_arr = output_arr[self.action_index: self.action_index + 2]
        presenter.print_subset_array(subset_arr)
        actions = list(Action)
        action_index = subset_arr.index(max(subset_arr))
        return actions[action_index]

    def decide_card_to_play_index(self, game_state: GameState) -> int:
        if not self.hand:
            return 0
        
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        subset_arr = output_arr[self.card_index: self.card_index + GameConstants.HAND_SIZE]
        
        # sort by network preference, then return first playable card
        card_preferences = sorted(range(len(subset_arr)), key=lambda i: subset_arr[i], reverse=True)
        
        for idx in card_preferences:
            if idx < len(self.hand) and self.hand[idx].can_be_played(game_state, self):
                return idx
        
        # fallback: return first playable card
        for i, card in enumerate(self.hand):
            if card.can_be_played(game_state, self):
                return i
        return 0

    def decide_cards_to_discard_indices(self, game_state: GameState) -> List[int]:
        if not self.hand:
            return []
        
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        # network outputs for discard count
        subset_arr = output_arr[self.discard_count_index: self.discard_count_index + GameConstants.HAND_SIZE]
        presenter.print_subset_array(subset_arr)
        discard_count = subset_arr.index(max(subset_arr)) + 1
        discard_count = min(discard_count, len(self.hand))  # can't discard more than we have

        # network outputs for which cards to discard
        subset_arr = output_arr[self.discard_index: self.discard_index + GameConstants.HAND_SIZE]
        presenter.print_subset_array(subset_arr)
        
        # get valid indices only
        valid_indices = list(range(len(self.hand)))
        discard_indices = sorted(valid_indices, key=lambda i: subset_arr[i] if i < len(subset_arr) else 0, reverse=True)
        return discard_indices[:discard_count]

    def decide_opponent(self, game_state: GameState, card) -> BasePlayer:
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        opponents = game_state.get_opponents(self)
        if not opponents:
            return None
        
        # use up to 5 opponent outputs (max 6 players game)
        num_opponent_outputs = min(self.MAX_OPPONENTS, len(output_arr) - self.opponent_index)
        subset_arr = output_arr[self.opponent_index: self.opponent_index + num_opponent_outputs]
        presenter.print_subset_array(subset_arr)

        # map network preference to actual opponents
        if len(opponents) <= num_opponent_outputs:
            # get preferences only for existing opponents
            valid_prefs = subset_arr[:len(opponents)]
            opponent_index = list(valid_prefs).index(max(valid_prefs))
            return opponents[opponent_index]
        else:
            # more opponents than outputs
            opponent_index = subset_arr.index(max(subset_arr))
            return opponents[opponent_index % len(opponents)]

    def decide_organ_color(self, game_state: GameState, opponent_body=None) -> CardColor:
        inputs = game_state.get_state_array_for_ai()
        output_arr = self.net.activate(inputs)
        presenter.print_output_array(output_arr)

        subset_arr = output_arr[self.color_index: self.color_index + len(CardColor)]
        
        # get available colors based on context
        if opponent_body:
            available_colors = [organ.color for organ in opponent_body]
        elif self.body:
            available_colors = [organ.color for organ in self.body]
        else:
            available_colors = list(CardColor)
        
        if not available_colors:
            available_colors = list(CardColor)
        
        # sort colors by network preference, return first available
        all_colors = list(CardColor)
        color_preferences = sorted(range(len(all_colors)), key=lambda i: subset_arr[i], reverse=True)
        
        for idx in color_preferences:
            if all_colors[idx] in available_colors:
                return all_colors[idx]
        
        # fallback
        return available_colors[0]

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

    def add_organ_to_body(self, organ: 'Organ') -> None:
        super().add_organ_to_body(organ)
        self.score += 10

    def remove_organ_from_body(self, organ):
        super().remove_organ_from_body(organ)
        self.score -= 10

    def discard_cards(self, game_state, card_ids):
        super().discard_cards(game_state, card_ids)
        self.score -= 10
