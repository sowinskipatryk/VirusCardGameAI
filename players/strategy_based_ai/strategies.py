from enums import CardType, TreatmentName, CardColor, OrganState
from players.base_player import BasePlayer
from game.game_state import GameState
from models.cards import Card
from models.move import Move

from typing import List, Tuple
from abc import ABC, abstractmethod


class CardPlayStrategy(ABC):
    @abstractmethod
    def apply(self, player: 'BasePlayer', game_state: 'GameState') -> Tuple[Card, List[Move]]:
        """Apply the strategy."""
        pass

    @abstractmethod
    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> Tuple[Card, List[Move]]:
        """Validate whether the strategy can be used."""
        pass


class OrganStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        organ_cards = [card for card in player.hand if card.type == CardType.ORGAN and card.can_be_played(game_state, player)]
        if not organ_cards:
            return
        return organ_cards[0], [Move()]

    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> bool:
        for card in player.hand:
            if card.type == CardType.ORGAN and card.can_be_played(game_state, player):
                return True
        return False


class OrganThiefStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.ORGAN_THIEF)
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

    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> bool:
        card = player.get_hand_card_by_name(TreatmentName.ORGAN_THIEF)
        if card and card.can_be_played(game_state, player):
            return True
        return False


class TransplantStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.TRANSPLANT)
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
            item[2].state - item[1].state,
            -item[2].state,
            -item[1].state
        ))

        best_choice = sorted_choices[0]

        return card, [Move(opponent=best_choice[0], player_organ=best_choice[2], opponent_organ=best_choice[1])]

    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> bool:
        card = player.get_hand_card_by_name(TreatmentName.TRANSPLANT)
        if card and card.can_be_played(game_state, player):
            return True
        return False


class MedicineStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        medicine_cards = [card for card in player.hand if card.type == CardType.MEDICINE and card.can_be_played(game_state, player)]
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

    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> bool:
        if not player.body:
            return False
        medicine_cards = [card for card in player.hand if card.type == CardType.MEDICINE and card.can_be_played(game_state, player)]
        for card in medicine_cards:
            if card and card.can_be_played(game_state, player):
                return True
        return False


class ContagionStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.CONTAGION)
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

    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> bool:
        card = player.get_hand_card_by_name(TreatmentName.CONTAGION)
        if card and card.can_be_played(game_state, player):
            return True
        return False


class VirusPlayStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        virus_cards = [card for card in player.hand if card.type == CardType.VIRUS and card.can_be_played(game_state, player)]
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

    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> bool:
        virus_cards = [card for card in player.hand if card.type == CardType.VIRUS and card.can_be_played(game_state, player)]
        for card in virus_cards:
            if card and card.can_be_played(game_state, player):
                return True
        return False


class MedicalErrorStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.MEDICAL_ERROR)
        all_players = game_state.get_opponents(player) + [player]
        sorted_players = sorted(all_players, key=lambda opponent: sum(organ.state for organ in opponent.body), reverse=True)
        best_player = sorted_players[0]
        if best_player is not player:
            return card, [Move(opponent=best_player)]

    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> bool:
        card = player.get_hand_card_by_name(TreatmentName.MEDICAL_ERROR)
        if card and card.can_be_played(game_state, player):
            return True
        return False


class LatexGloveStrategy(CardPlayStrategy):
    def apply(self, player, game_state):
        card = player.get_hand_card_by_name(TreatmentName.LATEX_GLOVE)
        return card, [Move()]

    def can_be_applied(self, player: 'BasePlayer', game_state: 'GameState') -> bool:
        card = player.get_hand_card_by_name(TreatmentName.LATEX_GLOVE)
        if card and card.can_be_played(game_state, player):
            return True
        return False
