from enums import CardType, TreatmentName, CardColor, OrganState, Action
from players.base_player import BasePlayer
from game.game_constants import GameConstants
from game.game_state import GameState
from models.cards import Card
from models.move import Move
from interface import presenter

from typing import List, Tuple
from abc import ABC, abstractmethod


class CardPlayStrategy(ABC):
    @abstractmethod
    def apply(self, player: 'BasePlayer', game_state: 'GameState') -> Tuple[Card, List[Move]]:
        """Check if this strategy can be applied."""
        pass


class WinningMoveStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        playable_cards = [card for card in player.hand if card.can_be_played(game_state, player)]

        for card in playable_cards:
            winning_moves = self.check_winning_moves(player, game_state, card)
            if winning_moves:
                return winning_moves

    def check_winning_moves(self, player: 'BasePlayer', game_state: GameState, card: Card):
        opponents = game_state.get_opponents(player)

        # if three organs are healthy we can check if organ or medicine will win the game
        player_healthy_organ_states = [organ.state for organ in player.body if organ.state >= OrganState.HEALTHY]
        moves_to_play = []
        if len(player_healthy_organ_states) >= 3:

            # check if we have the organ card of color that is not in the body
            if card.type == CardType.ORGAN and card.color not in player.organ_colors:
                moves_to_play.append(Move())
                return card, moves_to_play

            elif card.type == CardType.MEDICINE:
                # check if we have the medicine that is a wild card and any organ in the body is infected
                if card.color == CardColor.WILD:
                    for organ in player.body:
                        if organ.state == OrganState.INFECTED:
                            moves_to_play.append(Move(player_organ=organ))
                            return card, moves_to_play

                # OR check if we have the medicine card of color that is in the body and if the organ is infected
                elif card.color in player.organ_colors:
                    organ = player.get_organ_by_color(card.color)
                    if organ.state == OrganState.INFECTED:
                        moves_to_play.append(Move(player_organ=organ))
                        return card, moves_to_play

            # check if any opponent has healthy organ of color that is not in the body
            elif card.name == TreatmentName.ORGAN_THIEF:
                for opponent in opponents:
                    for opponent_organ in opponent.body:
                        if opponent_organ.color not in player.organ_colors and OrganState.HEALTHY <= opponent_organ.state < OrganState.IMMUNISED:
                            moves_to_play.append(Move(opponent=opponent, opponent_organ=opponent_organ))
                            return card, moves_to_play

            # check if any opponent has healthy organ of color that we can swap with infected organ of the same color OR other infected organ that is not in the opponent's body
            elif card.name == TreatmentName.TRANSPLANT:
                for opponent in opponents:
                    for opponent_organ in opponent.body:
                        if OrganState.HEALTHY <= opponent_organ.state < OrganState.IMMUNISED:
                            if opponent_organ.color == CardColor.WILD:
                                sorted_organs = sorted(player.body, key=lambda x: -len(x.viruses))
                                if sorted_organs[0].state < opponent_organ.state and sorted_organs[
                                    0].color not in opponent.organ_colors and opponent_organ.color not in player.organ_colors:
                                    moves_to_play.append(Move(opponent=opponent,
                                                              player_organ=sorted_organs[0],
                                                              opponent_organ=opponent_organ))
                                    return card, moves_to_play
                            else:
                                player_organ_same_color = player.get_organ_by_color(opponent_organ.color)
                                if player_organ_same_color and player_organ_same_color.state < opponent_organ.state:
                                    moves_to_play.append(Move(opponent=opponent,
                                                              player_organ=player_organ_same_color,
                                                              opponent_organ=opponent_organ))
                                    return card, moves_to_play

                                elif not player_organ_same_color:
                                    for player_organ in player.body:
                                        if player_organ.state < opponent_organ.state and player_organ.color not in opponent.organ_colors and opponent_organ.color not in player.organ_colors:
                                            moves_to_play.append(Move(opponent=opponent,
                                                                      player_organ=player_organ,
                                                                      opponent_organ=opponent_organ))
                                            return card, moves_to_play

        # check if we can get rid of viruses to get 4 healthy organs
        if card.name == TreatmentName.CONTAGION and len(player.body) >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN:
            healthy_organs = [organ for organ in player.body if organ.state >= OrganState.HEALTHY]
            infected_organs = [organ for organ in player.body if organ.state == OrganState.INFECTED]
            transmitted_viruses = []

            for player_organ in infected_organs:
                for opponent in opponents:
                    opponent_organ_same_color = opponent.get_organ_by_color(player_organ.color)
                    if opponent_organ_same_color and opponent_organ_same_color.state != OrganState.IMMUNISED:
                        transmitted_viruses.append((opponent, player_organ, opponent_organ_same_color))
                        break

                    # add logic for wild viruses

                if len(transmitted_viruses) + len(healthy_organs) >= GameConstants.NUM_HEALTHY_ORGANS_TO_WIN:
                    for transmitted_virus in transmitted_viruses:
                        opponent, player_organ, opponent_organ = transmitted_virus
                        moves_to_play.append(Move(opponent=opponent, player_organ=player_organ, opponent_organ=opponent_organ))

                    return card, moves_to_play


class OrganStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        organ_cards = [card for card in player.hand if card.type == CardType.ORGAN and card.can_be_played(game_state, player)]
        if not organ_cards:
            return
        return organ_cards[0], [Move()]


class OrganThiefStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.ORGAN_THIEF)
        if not card or not card.can_be_played(game_state, player):
            return

        opponents = game_state.get_opponents(player)
        valid_choices = [(opponent, organ) for opponent in opponents for organ in opponent.body if organ.color not in player.organ_colors and len(organ.medicines) < 2]
        if not valid_choices:
            return

        sorted_choices = sorted(valid_choices, key=lambda item: (
            -len(item[0].body),
            -len(item[1].medicines),
            len(item[1].viruses)))

        best_choice = sorted_choices[0]
        return card, [Move(opponent=best_choice[0], opponent_organ=best_choice[1])]


class TransplantStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.TRANSPLANT)
        if not card or not card.can_be_played(game_state, player):
            return

        opponents = game_state.get_opponents(player)
        valid_choices = [(opponent, opponent_organ, player_organ)
                         for opponent in opponents
                         for opponent_organ in opponent.body
                         for player_organ in player.body
                         if player_organ.state <= opponent_organ.state < OrganState.IMMUNISED
                         and player_organ.color not in opponent.organ_colors
                         and opponent_organ.color not in player.organ_colors]

        if not valid_choices:
            return

        sorted_choices = sorted(valid_choices, key=lambda item: (
            -len(item[0].body),
            -item[1].state,
            item[2].state - item[1].state))

        best_choice = sorted_choices[0]

        return card, [Move(opponent=best_choice[0], player_organ=best_choice[2], opponent_organ=best_choice[1])]


class MedicineStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        if not player.body:
            return

        medicine_cards = [card for card in player.hand if card.type == CardType.MEDICINE and card.can_be_played(game_state, player)]
        if not medicine_cards:
            return

        valid_choices = [(medicine_card, organ)
                         for organ in player.body
                         for medicine_card in medicine_cards
                         if medicine_card.color == organ.color
                         or organ.color == CardColor.WILD
                         or medicine_card.color == CardColor.WILD
                         and organ.state < OrganState.IMMUNISED]

        if not valid_choices:
            return

        sorted_choices = sorted(valid_choices, key=lambda item: (len(item[1].medicines),
                                                                 len(item[1].viruses)), reverse=True)

        best_choice = sorted_choices[0]
        return best_choice[0], [Move(player_organ=best_choice[1])]


class ContagionStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.CONTAGION)
        if not card or not card.can_be_played(game_state, player):
            return

        player_viruses = [(virus, organ) for organ in player.body for virus in organ.viruses]
        if not player_viruses:
            return

        opponents = game_state.get_opponents(player)

        valid_choices = [(virus, organ, opponent, opponent_organ)
                         for virus, organ in player_viruses
                         for opponent in opponents
                         for opponent_organ in opponent.body
                         if opponent_organ.state < OrganState.IMMUNISED
                         and virus.color == opponent_organ.color
                         or virus.color == CardColor.WILD
                         or (opponent_organ.color == CardColor.WILD and virus.color not in opponent.organ_colors)]

        if not valid_choices:
            return

        sorted_choices = sorted(valid_choices, key=lambda item: (len(item[2].body),
                                                                 len(item[3].medicines),
                                                                 len(item[3].viruses)), reverse=True)

        attack_capacity = {organ: organ.state for _, _, _, organ in sorted_choices}
        used_viruses = set()
        selected_moves = []

        for virus, organ, opponent, opponent_organ in sorted_choices:
            if virus in used_viruses:
                continue
            if attack_capacity[opponent_organ] <= 0:
                continue

            selected_moves.append(Move(player_organ=organ, opponent=opponent, opponent_organ=opponent_organ))
            used_viruses.add(virus)
            attack_capacity[opponent_organ] -= 1

        return card, selected_moves


class VirusPlayStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        virus_cards = [card for card in player.hand if card.type == CardType.VIRUS and card.can_be_played(game_state, player)]
        if not virus_cards:
            return

        opponents = game_state.get_opponents(player)
        valid_choices = [(virus_card, opponent, organ)
                         for virus_card in virus_cards
                         for opponent in opponents
                         for organ in opponent.body
                         if virus_card.color == organ.color
                         or organ.color == CardColor.WILD
                         or virus_card.color == CardColor.WILD
                         and organ.state < OrganState.IMMUNISED]

        if not valid_choices:
            return

        sorted_choices = sorted(valid_choices, key=lambda item: (len(item[1].body),
                                                                 len(item[2].medicines),
                                                                 len(item[2].viruses)), reverse=True)

        best_choice = sorted_choices[0]
        return best_choice[0], [Move(opponent=best_choice[1], opponent_organ=best_choice[2])]


class MedicalErrorStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.MEDICAL_ERROR)
        if not card or not card.can_be_played(game_state, player):
            return

        all_players = game_state.get_opponents(player) + [player]
        sorted_players = sorted(all_players, key=lambda opponent: sum(organ.state for organ in opponent.body), reverse=True)
        best_player = sorted_players[0]
        if best_player is not player:
            return card, [Move(opponent=best_player)]


class LatexGloveStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.LATEX_GLOVE)
        if card and card.can_be_played(game_state, player):
            return card, [Move()]


class RuleBasedAIPlayer(BasePlayer):
    def __init__(self, name: str):
        super().__init__(name)
        self.strategies = [
            WinningMoveStrategy(),
            MedicalErrorStrategy(),
            OrganStrategy(),
            OrganThiefStrategy(),
            TransplantStrategy(),
            MedicineStrategy(),
            ContagionStrategy(),
            VirusPlayStrategy(),
            LatexGloveStrategy()
        ]

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
        for strategy in self.strategies:
            if strategy.apply(self, game_state):
                best_moves = strategy.apply(self, game_state)
                if best_moves:
                    return best_moves

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

        # no need to discard latex glove (there is no condition to be played so just play it instead)
        # never discard medical error (too op, it won't stack player's hand as it is only one card)

        return card_ids

    # added to silence the abstract method warning
    def decide_opponent(self, game_state: GameState, card: Card) -> 'BasePlayer':
        pass

    def decide_organ_color(self, game_state: GameState, opponent_body=None) -> CardColor:
        pass

    def decide_action(self, game_state: GameState):
        pass
