from enums import CardType, Action, TreatmentName, CardColor, OrganState
from players.base_player import BasePlayer
from game_state import GameState
from cards import Card
from moves import Move

from typing import List, Tuple


class RuleBasedAIPlayer(BasePlayer):
    def __init__(self, name: str):
        super().__init__(name)

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
                            if player_organ.state < opponent_organ.state < OrganState.IMMUNISED:
                                if player_organ.color == opponent_organ.color:
                                    return Action.PLAY

                                if player_organ.color not in opponent.body_organ_colors and opponent_organ.color not in self.body_organ_colors:
                                    return Action.PLAY

        return Action.DISCARD

    def take_turn(self, game_state) -> bool:
        move_decision = self.decide_moves(game_state)
        if move_decision:
            card, moves = move_decision

            successful_moves = 0
            for move in moves:
                is_error = card.play(game_state, self, move)
                if not is_error:
                    successful_moves += 1
                    self.move_history.append((card.name, is_error))
                    assert len(self.body_organ_colors) == len(set(self.body_organ_colors))
            if successful_moves:
                self.remove_hand_card(card)
        else:
            card_ids = self.decide_cards_to_discard_indices(game_state)
            self.discard_cards(game_state, card_ids)

    def decide_moves(self, game_state: GameState) -> Tuple[Card, List[Move]]:
        opponents = game_state.get_opponents(self)

        # get playable cards to avoid unnecessary iterations
        playable_cards = [card for card in self.hand if card.can_be_played(game_state, self)]

        # rule 1 - check if there are any winning moves
        for card in playable_cards:
            winning_moves = self.check_winning_moves(game_state, card)
            if winning_moves:
                winning_card, moves_to_play = winning_moves
                return winning_card, moves_to_play

        moves_to_play = []

        # rule 2 - check if we have a medical error card and any opponent has 2+ organs that are of better health than ours
        medical_error_card = self.get_hand_card_by_name(TreatmentName.MEDICAL_ERROR)
        if medical_error_card:
            for opponent in opponents:
                if len(opponent.body) >= 2 and self.opponent_has_better_organs(opponent):
                    moves_to_play.append(Move(opponent=opponent))
                    return medical_error_card, moves_to_play

        # rule 3 - check if we have an organ card / organ thief card - same profit, same priority
        for card in playable_cards:
            if card.type == CardType.ORGAN:
                moves_to_play.append(Move())
                return card, moves_to_play

            elif card.name == TreatmentName.ORGAN_THIEF:
                sorted_opponents = sorted(opponents, key=lambda opponent: (sum(len(organ.medicines) for organ in opponent.body) == 2,
                                                                           any(organ_color not in self.get_organ_colors() for organ_color in self.body_organ_colors),
                                                                           -len(opponent.body),
                                                                           -sum(len(organ.medicines) for organ in opponent.body),
                                                                           sum(len(organ.viruses) for organ in opponent.body)))
                best_opponent = sorted_opponents[0]
                for opponent_organ in best_opponent.body:
                    if opponent_organ.color not in self.body_organ_colors:
                        moves_to_play.append(Move(opponent=best_opponent, opponent_organ=opponent_organ))
                        return card, moves_to_play

        # rule 4 - check if we have a transplant card
        transplant_card = self.get_hand_card_by_name(TreatmentName.TRANSPLANT)
        if transplant_card:
            filtered_opponents_and_organs = [(opponent, opponent_organ, player_organ) for opponent in opponents for opponent_organ in opponent.body for player_organ in self.body if opponent_organ.state != OrganState.IMMUNISED and player_organ.state != OrganState.IMMUNISED and player_organ.color not in opponent.body_organ_colors and opponent_organ.color not in self.body_organ_colors]
            #filtered_opponents_and_organs = [(opponent, opponent_organ, player_organ) for opponent, opponent_organ, player_organ in opponents_and_organs ]
            if filtered_opponents_and_organs:
                sorted_opponents_and_organs = sorted(filtered_opponents_and_organs, key=lambda item: (-item[1].state, -(item[1].state-item[2].state), -len(item[0].body)))

                best_move = sorted_opponents_and_organs[0]

                moves_to_play.append(Move(opponent=best_move[0], player_organ=best_move[2], opponent_organ=best_move[1]))

                return transplant_card, moves_to_play

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
                best_organ = sorted_filtered_organs[0]
                if wild_medicine:
                    chosen_medicine_card = next(card for card in medicine_cards if card.color == CardColor.WILD)
                else:
                    chosen_medicine_card = next(card for card in medicine_cards if card.color == best_organ.color)
                moves_to_play.append(Move(player_organ=best_organ))

                return chosen_medicine_card, moves_to_play

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
                    if sorted_opponents_and_organs:
                        best_move = sorted_opponents_and_organs[0]
                        player_organ = next(organ for organ in self.body for curr_virus in organ.viruses if curr_virus is virus)

                        moves_to_play.append(Move(opponent=best_move[0], player_organ=player_organ, opponent_organ=best_move[1]))

                        transmitted_viruses += 1

                if transmitted_viruses:
                    return contagion_card, moves_to_play

        # rule 7 - check if we have viruses and play if possible
        virus_cards = [card for card in playable_cards if card.type == CardType.VIRUS]
        opponents_and_organs = [(opponent, organ) for opponent in opponents for organ in opponent.body if organ.state != OrganState.IMMUNISED]
        if opponents_and_organs:
            sorted_opponents_and_organs = sorted(opponents_and_organs, key=lambda item: (-len(item[0].body), item[1].state))
            for element in sorted_opponents_and_organs:
                for virus_card in virus_cards:
                    if element[1].color == CardColor.WILD and virus_card.color in element[0].body_organ_colors:
                        continue
                    if element[1].color in [virus_card.color, CardColor.WILD]:
                        moves_to_play.append(Move(opponent=element[0], opponent_organ=element[1]))
                        return virus_card, moves_to_play

                    elif virus_card.color == CardColor.WILD:
                        moves_to_play.append(Move(opponent=element[0], opponent_organ=element[1]))
                        return virus_card, moves_to_play

        # rule 8 (last resort move) - check if we have a latex glove card and play it
        latex_glove_card = self.get_hand_card_by_name(TreatmentName.LATEX_GLOVE)
        if latex_glove_card:
            moves_to_play.append(Move())
            return latex_glove_card, moves_to_play

        # at this point we probably have only one playable card and it's medical error that we don't want to play
        if len(playable_cards) == 1 and playable_cards[0].type == TreatmentName.MEDICAL_ERROR:
            return

        # raise ValueError("Something went wrong")

    def decide_cards_to_discard_indices(self, game_state: GameState) -> List[int]:
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
        player_healthy_organ_states = [organ.state for organ in self.body if organ.state >= OrganState.HEALTHY]
        moves_to_play = []
        if len(player_healthy_organ_states) >= 3:

            # check if we have the organ card of color that is not in the body
            if card.type == CardType.ORGAN and card.color not in self.body_organ_colors:
                moves_to_play.append(Move())
                return card, moves_to_play

            elif card.type == CardType.MEDICINE:
                # check if we have the medicine that is a wild card and any organ in the body is infected
                if card.color == CardColor.WILD:
                    for organ in self.body:
                        if organ.state == OrganState.INFECTED:
                            moves_to_play.append(Move(player_organ=organ))
                            return card, moves_to_play

                # OR check if we have the medicine card of color that is in the body and if the organ is infected
                elif card.color in self.body_organ_colors:
                    organ = self.get_organ_by_color(card.color)
                    if organ.state == OrganState.INFECTED:
                        moves_to_play.append(Move(player_organ=organ))
                        return card, moves_to_play

            # check if any opponent has healthy organ of color that is not in the body
            elif card.name == TreatmentName.ORGAN_THIEF:
                for opponent in opponents:
                    for opponent_organ in opponent.body:
                        if opponent_organ.color not in self.body_organ_colors and OrganState.HEALTHY <= opponent_organ.state < OrganState.IMMUNISED:
                            moves_to_play.append(Move(opponent=opponent, opponent_organ=opponent_organ))
                            return card, moves_to_play

            # check if any opponent has healthy organ of color that we can swap with infected organ of the same color OR other infected organ that is not in the opponent's body
            elif card.name == TreatmentName.TRANSPLANT:
                for opponent in opponents:
                    for opponent_organ in opponent.body:
                        if OrganState.HEALTHY <= opponent_organ.state < OrganState.IMMUNISED:
                            if opponent_organ.color == CardColor.WILD:
                                sorted_organs = sorted(self.body, key=lambda x: -len(x.viruses))
                                if sorted_organs[0].state < opponent_organ.state and sorted_organs[0].color not in opponent.body_organ_colors and opponent_organ.color not in self.body_organ_colors:
                                    moves_to_play.append(Move(opponent=opponent,
                                                              player_organ=sorted_organs[0],
                                                              opponent_organ=opponent_organ))
                                    return card, moves_to_play
                            else:
                                player_organ_same_color = self.get_organ_by_color(opponent_organ.color)
                                if player_organ_same_color and player_organ_same_color.state < opponent_organ.state:
                                    moves_to_play.append(Move(opponent=opponent,
                                                      player_organ=player_organ_same_color,
                                                      opponent_organ=opponent_organ))
                                    return card, moves_to_play

                                elif not player_organ_same_color:
                                    for player_organ in self.body:
                                        if player_organ.state < opponent_organ.state and player_organ.color not in opponent.body_organ_colors and opponent_organ.color not in self.body_organ_colors:
                                            moves_to_play.append(Move(opponent=opponent,
                                                              player_organ=player_organ,
                                                              opponent_organ=opponent_organ))
                                            return card, moves_to_play

        # check if we can get rid of viruses to get 4 healthy organs
        from game_config import GameConfig
        if card.name == TreatmentName.CONTAGION and len(self.body) >= GameConfig.num_organs_to_win:
            healthy_organs = [organ for organ in self.body if organ.state >= OrganState.HEALTHY]
            infected_organs = [organ for organ in self.body if organ.state == OrganState.INFECTED]
            transmitted_viruses = []

            for player_organ in infected_organs:
                for opponent in opponents:
                    opponent_organ_same_color = opponent.get_organ_by_color(player_organ.color)
                    if opponent_organ_same_color and opponent_organ_same_color.state != OrganState.IMMUNISED:
                            transmitted_viruses.append((opponent, player_organ, opponent_organ_same_color))
                            break

                    # add logic for wild viruses

                if len(transmitted_viruses) + len(healthy_organs) >= GameConfig.num_organs_to_win:
                    for transmitted_virus in transmitted_viruses:
                        opponent, player_organ, opponent_organ = transmitted_virus
                        moves_to_play.append(Move(opponent=opponent, player_organ=player_organ, opponent_organ=opponent_organ))

                    return card, moves_to_play

    def check_move_with_maximum_profit(self):
        # 1 - immunised organs
        # 2 - rest organs
        # 3 - state
        pass

    # added to silence the abstract method warning
    def decide_opponent(self, game_state: GameState, card: Card) -> 'BasePlayer':
        pass

    def decide_organ_color(self, game_state: GameState, opponent_body=None) -> CardColor:
        pass
