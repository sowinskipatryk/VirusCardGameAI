from enums import CardType, Action, TreatmentName, CardColor, OrganState
from players.base_player import BasePlayer
from game_state import GameState
from cards import Card

from typing import List


class RuleBasedAIPlayer(BasePlayer):
    def __init__(self, name: str):
        super().__init__(name)
        self.decided_opponents = []
        self.decided_player_card_colors = []
        self.decided_opponent_card_colors = []

    def decide_action(self, game_state: GameState):
        opponents = game_state.get_opponents(self)

        for card in self.hand:
            # play organ, medicine, virus cards whenever we can
            if card.type in [CardType.ORGAN, CardType.MEDICINE, CardType.VIRUS] and card.can_be_played(game_state, self):
                return Action.PLAY

            # play contagion, organ thief cards whenever we can
            # play latex glove whenever we can just to get rid of it and cause chaos in the opponents
            if card.name in [TreatmentName.CONTAGION, TreatmentName.ORGAN_THIEF, TreatmentName.LATEX_GLOVE] and card.can_be_played(game_state, self):
                return Action.PLAY

            # play medical error if any opponent has more organs than we do OR if theirs have better states
            if card.name == TreatmentName.MEDICAL_ERROR:
                for opponent in opponents:

                    # not worth it to play medical error if opponent has less than two organs
                    if len(opponent.body) < 2:
                        continue

                    if self.opponent_has_better_organs(opponent):
                        return Action.PLAY

            # play transplant card if our organ state is worse than the organ state of the opponent
            if card.name == TreatmentName.TRANSPLANT:
                fine_organ_states = [OrganState.IMMUNISED, OrganState.VACCINATED]
                candidate_organs = [organ for organ in self.body if organ.state not in fine_organ_states]
                for player_organ in candidate_organs:
                    for opponent in opponents:
                        for opponent_organ in opponent.body:
                            # the opponent's organ must be better AND swapped organs must be either of the same color or not in each other's bodies
                            if player_organ.state < opponent_organ.state:
                                if player_organ.color == opponent_organ.color:
                                    return Action.PLAY

                                opponent_organ_colors = [opponent_organ.color for opponent_organ in opponent.body]
                                player_organ_colors = [player_organ.color for player_organ in self.body]
                                if player_organ.color not in opponent_organ_colors and opponent_organ.color not in player_organ_colors:
                                    return Action.PLAY

        return Action.DISCARD


    def decide_opponent(self, game_state: GameState, card):
        return self.decided_opponents.pop()

    def decide_organ_color(self, game_state: GameState, target_body=None):
        if target_body:
            return self.decided_opponent_card_colors.pop()
        return self.decided_player_card_colors.pop()

    def decide_card_to_play(self, game_state: GameState) -> int:
        if self.decided_opponents or self.decided_player_card_colors or self.decided_opponent_card_colors:
            raise ValueError('Implementation error. Each list should be empty')

        opponents = game_state.get_opponents(self)

        # get playable cards to avoid unnecessary iterations
        playable_cards = [card for card in self.hand if card.can_be_played(game_state, self)]

        # rule 1 - check if there are any winning moves
        for card in playable_cards:
            winning_card = self.check_winning_moves(game_state, card)
            if winning_card:
                return self.hand.index(winning_card)

        # rule 2 - check if we have a medical error card and any opponent has 2+ organs that are of better health than ours
        medical_error_card = self.get_hand_card_by_name(TreatmentName.MEDICAL_ERROR)
        if medical_error_card:
            for opponent in opponents:
                if len(opponent.body) >= 2 and self.opponent_has_better_organs(opponent):
                    self.decided_opponents.append(opponent)
                    return self.hand.index(medical_error_card)

        # rule 3 - check if we have an organ card / organ thief card - same profit, same priority
        for card in playable_cards:
            if card.type == CardType.ORGAN:
                return self.hand.index(card)

            elif card.name == TreatmentName.ORGAN_THIEF:
                sorted_opponents = sorted(opponents, key=lambda opponent: (any(organ_color not in self.get_organ_colors() for organ_color in self.body_organ_colors),
                                                                           -len(opponent.body),
                                                                           -sum(len(organ.medicines) for organ in opponent.body),
                                                                           sum(len(organ.viruses) for organ in opponent.body)))
                best_opponent = sorted_opponents[0]
                for opponent_organ in best_opponent.body:
                    if opponent_organ.color not in self.body:
                        self.decided_opponents.append(best_opponent)
                        self.decided_opponent_card_colors.append(opponent_organ.color)
                        return self.hand.index(card)

        # rule 4 - check if we have a transplant card
        transplant_card = self.get_hand_card_by_name(TreatmentName.TRANSPLANT)
        if transplant_card:
            opponents_and_organs = [(opponent, opponent_organ, player_organ) for opponent in opponents for opponent_organ in opponent.body for player_organ in self.body]
            filtered_opponents_and_organs = [(opponent, opponent_organ, player_organ) for opponent, opponent_organ, player_organ in opponents_and_organs if opponent_organ.state != OrganState.IMMUNISED and player_organ.state != OrganState.IMMUNISED]
            if filtered_opponents_and_organs:
                sorted_opponents_and_organs = sorted(filtered_opponents_and_organs, key=lambda item: (-item[1].state, -(item[1].state-item[2].state), -len(item[0].body)))

                best_move = sorted_opponents_and_organs[0]

                self.decided_opponents.append(best_move[0])
                self.decided_player_card_colors.append(best_move[1].color)
                self.decided_opponent_card_colors.append(best_move[2].color)

                return self.hand.index(transplant_card)

        # rule 5 - check if we have a medicine card - prioritize vaccinated organs, then infected ones
        medicine_cards = [card for card in playable_cards if card.type == CardType.MEDICINE]
        if medicine_cards:
            if any(medicine_card.color == CardColor.WILD for medicine_card in medicine_cards):
                matching_organs = self.body
                wild_medicine = True
            else:
                matching_organs = [self.get_organ_by_color(medicine_card.color) for medicine_card in medicine_cards]
                wild_medicine = False
            filtered_organs = [organ for organ in matching_organs if organ.state != OrganState.IMMUNISED]
            if filtered_organs:
                sorted_filtered_organs = sorted(filtered_organs, key=lambda x: (len(x.medicines) > 0, len(x.viruses) > 0), reverse=True)
                best_organ_color = sorted_filtered_organs[0].color
                if wild_medicine:
                    chosen_medicine_card = next(card for card in medicine_cards if card.color == CardColor.WILD)
                else:
                    chosen_medicine_card = next(card for card in medicine_cards if card.color == best_organ_color)
                if chosen_medicine_card.color == CardColor.WILD:
                    self.decided_player_card_colors.append(best_organ_color)

                return self.hand.index(chosen_medicine_card)

        # rule 6 - check if we have a contagion card
        contagion_card = self.get_hand_card_by_name(TreatmentName.CONTAGION)
        if contagion_card:
            viruses = [virus for organ in self.body for virus in organ.viruses]
            opponents_and_organs = [(opponent, opponent_organ) for opponent in opponents for opponent_organ in opponent.body if opponent_organ.state != OrganState.IMMUNISED]
            if opponents_and_organs:
                transmitted_viruses = 0
                for virus in viruses:
                    if virus.color == CardColor.WILD:
                        filtered_opponents_and_organs = [(opponent, opponent_organ) for opponent, opponent_organ in opponents_and_organs]
                    else:
                        filtered_opponents_and_organs = [(opponent, opponent_organ) for opponent, opponent_organ in opponents_and_organs if virus.color in opponent.body_organ_colors]
                    sorted_opponents_and_organs = sorted(filtered_opponents_and_organs, key=lambda item: (-len(item[1].viruses), -len(item[1].medicines), -len(item[0].body)))
                    best_move = sorted_opponents_and_organs[0]

                    self.decided_opponents.append(best_move[0])
                    self.decided_opponent_card_colors.append(best_move[1].color)
                    if virus.color == CardColor.WILD:
                        self.decided_player_card_colors.append(virus.color)

                    transmitted_viruses += 1

                if transmitted_viruses:
                    return self.hand.index(contagion_card)

        # rule 7 - check if we have viruses and play if possible
        virus_cards = [card for card in playable_cards if card.type == CardType.VIRUS]
        opponents_and_organs = [(opponent, organ) for opponent in opponents for organ in opponent.body if organ.state != OrganState.IMMUNISED]
        if opponents_and_organs:
            sorted_opponents_and_organs = sorted(opponents_and_organs, key=lambda item: (-len(item[0].body), item[1].state))
            for element in sorted_opponents_and_organs:
                for virus_card in virus_cards:
                    if element[1].color in [virus_card.color, CardColor.WILD]:
                        self.decided_opponents.append(element[0])
                        return self.hand.index(virus_card)

                    elif virus_card.color == CardColor.WILD:
                        self.decided_opponents.append(element[0])
                        self.decided_opponent_card_colors.append(element[1].color)
                        return self.hand.index(virus_card)

        # rule 8 (last resort move) - check if we have a latex glove card and play it
        latex_glove_card = self.get_hand_card_by_name(TreatmentName.LATEX_GLOVE)
        if latex_glove_card:
            return self.hand.index(latex_glove_card)

        raise ValueError('No card picked')

    def decide_cards_to_discard(self, game_state: GameState) -> List[int]:
        card_ids = []
        for i, card in enumerate(self.hand):
            if card.type in [CardType.ORGAN, CardType.MEDICINE, CardType.VIRUS] and not card.can_be_played(game_state, self):
                    card_ids.append(i)

            if card.name in [TreatmentName.CONTAGION, TreatmentName.TRANSPLANT] and not card.can_be_played(game_state, self):
                    card_ids.append(i)

        # try not to discard organ thief (too op) or latex glove (just play it instead) - discard them only if no cards were chosen
        if not card_ids:
            for i, card in enumerate(self.hand):
                if card.name == TreatmentName.LATEX_GLOVE:
                    return [i]

        if not card_ids:
            for i, card in enumerate(self.hand):
                if card.name == TreatmentName.ORGAN_THIEF:
                    return [i]

        # never discard medical error (too op)

        return card_ids

    def opponent_has_better_organs(self, opponent):
        player_organ_states = [organ.state for organ in self.body]
        opponent_organ_states = [organ.state for organ in opponent.body]

        if len(opponent_organ_states) > len(player_organ_states):
            return True

        player_organs_immunised = player_organ_states.count(OrganState.IMMUNISED)
        opponent_organs_immunised = opponent_organ_states.count(OrganState.IMMUNISED)

        if player_organs_immunised > opponent_organs_immunised:
            return False

        if opponent_organs_immunised > player_organs_immunised:
            return True

        player_sum = sum(player_organ_states)
        opponent_sum = sum(opponent_organ_states)
        if opponent_sum > player_sum:
            return True

    def check_winning_moves(self, game_state: GameState, card: Card):
        opponents = game_state.get_opponents(self)

        # if three organs are healthy we can check if organ or medicine will win the game
        healthy_organ_states = [organ.state for organ in self.body if organ.state >= OrganState.HEALTHY]
        if len(healthy_organ_states) >= 3:

            # check if we have the organ card of color that is not in the body
            if card.type == CardType.ORGAN and card.color not in self.body_organ_colors:
                return card

            # check if we have the medicine card of color that is in the body and if the organ is infected
            if card.type == CardType.MEDICINE:
                if card.color in self.body_organ_colors:
                    opponent_organ = self.get_organ_by_color(card.color)
                    if opponent_organ.state == OrganState.INFECTED:
                        return card

                # OR if it is a wild card and any organ in the body is infected
                if card.color == CardColor.WILD:
                    for organ in self.body:
                        if organ.state == OrganState.INFECTED:
                            self.decided_player_card_colors.append(organ.color)
                            return card

            # check if any opponent has healthy organ of color that is not in the body
            if card.name == TreatmentName.ORGAN_THIEF:
                for opponent in opponents:
                    for opponent_organ in opponent.body:
                        if opponent_organ.color not in self.body_organ_colors and opponent_organ.state >= OrganState.HEALTHY:
                            self.decided_opponents.append(opponent)
                            self.decided_opponent_card_colors.append(opponent_organ.color)
                            return card

            # check if any opponent has healthy organ of color that we can swap with infected organ of the same color OR other infected organ that is not in the opponent's body
            if card.name == TreatmentName.TRANSPLANT:
                for opponent in opponents:
                    for opponent_organ in opponent.body:
                        if opponent_organ.state >= OrganState.HEALTHY:
                            player_organ_same_color = self.get_organ_by_color(opponent_organ.color)
                            if player_organ_same_color and player_organ_same_color.state == OrganState.INFECTED:
                                self.decided_opponents.append(opponent)
                                self.decided_opponent_card_colors.append(opponent_organ.color)
                                self.decided_player_card_colors.append(player_organ_same_color.color)
                                return card

                            if not player_organ_same_color:
                                for player_organ in self.body:
                                    if player_organ.state == OrganState.INFECTED and player_organ.color not in opponent.body_organ_colors:
                                        self.decided_opponents.append(opponent)
                                        self.decided_opponent_card_colors.append(opponent_organ.color)
                                        self.decided_player_card_colors.append(player_organ.color)
                                        return card

        # check if we can get rid of viruses to get 4 healthy organs
        if card.name == TreatmentName.CONTAGION and len(self.body) >= 4: # GameConfig.num_organs_to_win:
            healthy_organs = [organ for organ in self.body if organ.state >= OrganState.HEALTHY]
            infected_organs = [organ for organ in self.body if organ.state == OrganState.INFECTED]
            transmitted_viruses = []

            for player_organ in infected_organs:
                for opponent in opponents:
                    opponent_organ_same_color = opponent.get_organ_by_color(player_organ.color)
                    if opponent_organ_same_color and opponent_organ_same_color.state != OrganState.IMMUNISED:
                            transmitted_viruses.append((opponent, player_organ.color, opponent_organ_same_color.color))
                            break

                    # add logic for wild viruses

                from game_config import GameConfig
                if len(transmitted_viruses) + len(healthy_organs) >= GameConfig.num_organs_to_win:
                    for transmitted_virus in transmitted_viruses:
                        opponent, player_color, opponent_color = transmitted_virus
                        self.decided_opponents.append(opponent)
                        self.decided_opponent_card_colors.append(opponent_color)
                        self.decided_player_card_colors.append(player_color)

                    return card

    def check_move_with_maximum_profit(self):
        # 1 - immunised organs
        # 2 - rest organs
        # 3 - state
        pass
