import copy
from typing import List, Optional, Tuple

from game.enums import Action, CardType, TreatmentName, CardColor, OrganState
from game.state import GameState
from game.interface import presenter
from game.models.cards import Card
from game.models.move import Move
from game.constants import GameConstants
from game.players import BasePlayer
from game.players.strategy_based_ai.strategies import (MedicalErrorStrategy, OrganStrategy, OrganThiefStrategy,
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

    def _check_winning_move(self, game_state: GameState) -> Optional[Tuple[Card, List[Move]]]:
        healthy_organs = [o for o in self.body if o.state >= OrganState.HEALTHY]
        num_healthy = len(healthy_organs)
        
        # need at least 3 healthy organs to potentially win this turn
        if num_healthy < GameConstants.NUM_HEALTHY_ORGANS_TO_WIN - 1:
            return None
        
        # scenario 1: play organ card to get 4th healthy organ
        if num_healthy == GameConstants.NUM_HEALTHY_ORGANS_TO_WIN - 1:
            for card in self.hand:
                if card.type == CardType.ORGAN and card.can_be_played(game_state, self):
                    if card.color not in self.organ_colors:
                        return card, [Move()]
        
        # scenario 2: cure infected organ with medicine to get 4th healthy
        infected_organs = [o for o in self.body if o.state == OrganState.INFECTED]
        if num_healthy == GameConstants.NUM_HEALTHY_ORGANS_TO_WIN - 1 and infected_organs:
            for card in self.hand:
                if card.type == CardType.MEDICINE:
                    for infected in infected_organs:
                        if card.color in [infected.color, CardColor.WILD] or infected.color == CardColor.WILD:
                            return card, [Move(player_organ=infected)]
        
        # scenario 3: steal healthy organ from opponent
        if num_healthy == GameConstants.NUM_HEALTHY_ORGANS_TO_WIN - 1:
            organ_thief = self.get_hand_card_by_name(TreatmentName.ORGAN_THIEF)
            if organ_thief and organ_thief.can_be_played(game_state, self):
                for opponent in game_state.get_opponents(self):
                    for organ in opponent.body:
                        if (organ.color not in self.organ_colors and
                            OrganState.HEALTHY <= organ.state < OrganState.IMMUNISED):
                            return organ_thief, [Move(opponent=opponent, opponent_organ=organ)]
        
        # scenario 4: use contagion to cure multiple infected organs
        contagion = self.get_hand_card_by_name(TreatmentName.CONTAGION)
        if contagion and contagion.can_be_played(game_state, self):
            infected_count = len(infected_organs)
            if num_healthy + infected_count >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN:
                # check if we can transfer enough viruses
                moves = []
                # track viruses used to avoid transferring same virus twice
                virus_count_per_organ = {organ: len(organ.viruses) for organ in infected_organs}
                
                for infected in infected_organs:
                    if not infected.viruses:
                        continue
                    for _ in range(virus_count_per_organ[infected]):
                        if virus_count_per_organ[infected] <= 0:
                            break
                        virus = infected.viruses[0]  # will be removed after each transfer
                        found_target = False
                        for opponent in game_state.get_opponents(self):
                            for opp_organ in opponent.body:
                                if (opp_organ.state < OrganState.IMMUNISED and
                                    (virus.color in [opp_organ.color, CardColor.WILD] or 
                                     opp_organ.color == CardColor.WILD)):
                                    moves.append(Move(player_organ=infected, opponent=opponent, opponent_organ=opp_organ))
                                    virus_count_per_organ[infected] -= 1
                                    found_target = True
                                    break
                            if found_target:
                                break
                    if len(moves) >= infected_count:
                        break
                
                if len(moves) + num_healthy >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN:
                    return contagion, moves
        
        return None

    def _should_avoid_strategy(self, strategy, game_state: GameState) -> bool:
        # check if a strategy should be avoided in current situation (it is counterproductive).
        healthy_organs = [o for o in self.body if o.state >= OrganState.HEALTHY]
        num_healthy = len(healthy_organs)
        
        # don't play Medical Error if we're close to winning
        if isinstance(strategy, MedicalErrorStrategy):
            # avoid if we have 3+ healthy organs (we're winning!)
            if num_healthy >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN - 1:
                return True
            
            # avoid if we have more/better organs than opponents
            opponents = game_state.get_opponents(self)
            my_score = sum(o.state for o in self.body)
            for opponent in opponents:
                opp_score = sum(o.state for o in opponent.body)
                if opp_score > my_score:
                    return False  # opponent has better body, Medical Error might be good
            return True  # we have the best body, don't swap
        
        # don't play Latex Glove if we're about to win
        if isinstance(strategy, LatexGloveStrategy):
            if num_healthy >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN - 1:
                # check if we have a winning card in hand
                for card in self.hand:
                    if card.type == CardType.ORGAN and card.color not in self.organ_colors:
                        return True  # play the organ instead
        
        return False

    def evaluate_moves(self, game_state, card, moves) -> int:
        score = 0
        opponents = game_state.get_opponents(self)
        
        # calculate state BEFORE move
        for opponent in opponents:
            for organ in opponent.body:
                score += organ.state

        for organ in self.body:
            score -= organ.state

        # simulate move
        self.play_card(game_state, card, moves)

        # calculate state AFTER move
        for opponent in opponents:
            for organ in opponent.body:
                score -= organ.state

        for organ in self.body:
            score += organ.state

        # huge bonus for winning
        if game_state.check_win_condition(self):
            score += 1000
        
        # bonus for getting closer to winning
        healthy_after = len([o for o in self.body if o.state >= OrganState.HEALTHY])
        score += healthy_after * 10
        
        # bonus for immunised organs
        immunised = len([o for o in self.body if o.state == OrganState.IMMUNISED])
        score += immunised * 5
        
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

    def prepare_moves(self, game_state) -> Optional[Tuple[Card, List[Move]]]:
        # priority 1: check for immediate winning move
        winning_move = self._check_winning_move(game_state)
        if winning_move:
            return winning_move
        
        # priority 2: evaluate all applicable strategies and pick best
        valid_strategies = [
            strategy for strategy in self.strategies 
            if strategy.can_be_applied(self, game_state) 
            and not self._should_avoid_strategy(strategy, game_state)
        ]
        
        if not valid_strategies:
            return None

        scored_strategies = []
        for strategy in valid_strategies:
            # simulate on copied state
            new_game_state = copy.deepcopy(game_state)
            new_game_state.current_player_index = game_state.current_player_index
            new_player = new_game_state.get_current_player()
            
            result = strategy.apply(new_player, new_game_state)
            if not result:
                continue
            card, moves = result
            score = new_player.evaluate_moves(new_game_state, card, moves)
            scored_strategies.append((score, strategy))

        if not scored_strategies:
            return None

        # sort by score and pick best
        sorted_strategies = sorted(scored_strategies, key=lambda x: x[0], reverse=True)
        best_score, best_strategy = sorted_strategies[0]
        
        # apply best strategy on actual game state
        result = best_strategy.apply(self, game_state)
        return result

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

    # these methods are not used since StrategyBasedAIPlayer overrides take_turn()
    # and uses strategies directly. added to satisfy abstract base class.
    def decide_opponent(self, game_state: GameState, card: Card) -> 'BasePlayer':
        raise NotImplementedError(
            "StrategyBasedAIPlayer uses strategies instead of decide_opponent."
        )

    def decide_organ_color(self, game_state: GameState, opponent_body=None) -> CardColor:
        raise NotImplementedError(
            "StrategyBasedAIPlayer uses strategies instead of decide_organ_color."
        )

    def decide_action(self, game_state: GameState) -> Action:
        raise NotImplementedError(
            "StrategyBasedAIPlayer uses strategies instead of decide_action."
        )
