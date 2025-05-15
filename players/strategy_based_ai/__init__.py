import copy
from typing import List

from enums import Action, CardType, TreatmentName, CardColor
from game.game_state import GameState
from interface import presenter
from models.cards import Card
from players import BasePlayer
from players.strategy_based_ai.strategies import (MedicalErrorStrategy, OrganStrategy, OrganThiefStrategy,
                                                  TransplantStrategy, MedicineStrategy, ContagionStrategy,
                                                  VirusPlayStrategy, LatexGloveStrategy)


class StrategyBasedAIPlayer(BasePlayer):
    def __init__(self, name: str):
        super().__init__(name)
        self.strategies = [
            MedicalErrorStrategy(),
            OrganStrategy(),
            OrganThiefStrategy(),
            TransplantStrategy(),
            MedicineStrategy(),
            ContagionStrategy(),
            VirusPlayStrategy(),
            LatexGloveStrategy()
        ]

    def evaluate_moves(self, game_state, card, moves):
        score = 0
        opponents = game_state.get_opponents(self)
        for opponent in opponents:
            for organ in opponent.body:
                score += organ.state

        for organ in self.body:
            score -= organ.state

        self.play_card(game_state, card, moves)

        for opponent in opponents:
            for organ in opponent.body:
                score -= organ.state

        for organ in self.body:
            score += organ.state

        if game_state.check_win_condition(self):
            score += 100
        return score

    def take_turn(self, game_state) -> bool:
        best_moves = self.prepare_moves(game_state)
        if best_moves:
            card, moves = best_moves
            presenter.print_decision(Action.PLAY)
            presenter.print_card(card)
            self.play_card(game_state, card, moves)
        else:
            presenter.print_decision(Action.DISCARD)
            card_ids = self.decide_cards_to_discard_indices(game_state)
            self.discard_cards(game_state, card_ids)

    def prepare_moves(self, game_state):
        valid_strategies = [strategy for strategy in self.strategies if strategy.can_be_applied(self, game_state)]
        if not valid_strategies:
            return

        scored_strategies = []
        for strategy in valid_strategies:
            new_game_state = copy.deepcopy(game_state)
            new_game_state.current_player_index = game_state.current_player_index
            new_player = new_game_state.get_current_player()
            result = strategy.apply(new_player, new_game_state)
            if not result:
                return
            card, moves = result
            score = new_player.evaluate_moves(new_game_state, card, moves)
            scored_strategies.append((score, strategy, card, moves))

        if not scored_strategies:
            return

        sorted_strategies = sorted(scored_strategies, key=lambda x: x[0], reverse=True)
        best_score, best_strategy, best_card, best_moves = sorted_strategies[0]
        result = best_strategy.apply(self, game_state)
        if not result:
            return
        orig_card, orig_moves = result
        return orig_card, orig_moves

    def decide_cards_to_discard_indices(self, game_state: GameState) -> List[int]:
        card_ids = []
        for i, card in enumerate(self.hand):
            if card.type in [CardType.ORGAN, CardType.MEDICINE, CardType.VIRUS] and not card.can_be_played(game_state, self):
                card_ids.append(i)

            if card.name in [TreatmentName.CONTAGION, TreatmentName.TRANSPLANT] and not card.can_be_played(game_state, self):
                card_ids.append(i)

        if not card_ids:
            for i, card in enumerate(self.hand):
                if card.name == TreatmentName.ORGAN_THIEF:
                    return [i]

        # no need to discard latex glove (just play it instead)
        # never discard medical error (too op, it won't stack player's hand as there is only one card in deck)

        return card_ids

    # added to silence the abstract method warning
    def decide_opponent(self, game_state: GameState, card: Card) -> 'BasePlayer':
        pass

    def decide_organ_color(self, game_state: GameState, opponent_body=None) -> CardColor:
        pass

    def decide_action(self, game_state: GameState):
        pass
