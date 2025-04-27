from abc import ABC, abstractmethod
from typing import List
from enums import TreatmentName, CardType, OrganState, CardColor
from models.move import Move
from models.organ_states import HealthyStateHandler


class Card(ABC):
    def __init__(self, name: str, card_type: CardType):
        self.name = str(name)
        self.type = card_type

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> CardType:
        return self.type

    @abstractmethod
    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool: ...

    @abstractmethod
    def can_be_played(self, game_state: 'GameState', owner: 'Player') -> bool: ...

    @abstractmethod
    def prepare_moves(self, player, game_state) -> List[Move]: ...

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class ColoredCard(Card, ABC):
    def __init__(self, card_type: CardType, color: CardColor):
        name = f"{card_type.value} {color.value}"
        super().__init__(name, card_type)
        self.color = color


class Medicine(ColoredCard):
    def __init__(self, color: CardColor):
        self.name = f"{color} {CardType.MEDICINE}"
        super().__init__(CardType.MEDICINE, color)

    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool:
        target_organ = move.player_organ
        if not target_organ:
            return True

        return target_organ.state_handler.on_medicine_play(
            medicine_card=self,
            target_organ=target_organ,
            game_state=game_state
        )

    def can_be_played(self, game_state: 'GameState', owner: 'Player'):
        for organ in owner.body:
            if organ.state != OrganState.IMMUNISED and self.color in [organ.color, CardColor.WILD]:
                return True

    def prepare_moves(self, player, game_state) -> List[Move]:
        if self.color == CardColor.WILD or any(organ.color == CardColor.WILD for organ in player.body):
            chosen_color = player.decide_organ_color(game_state)
        else:
            chosen_color = self.color
        chosen_organ = player.get_organ_by_color(chosen_color)
        if chosen_organ:
            return [Move(player_organ=chosen_organ)]


class Virus(ColoredCard):
    def __init__(self, color):
        self.name = f"{color} {CardType.VIRUS}"
        super().__init__(CardType.VIRUS, color)

    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool:
        target_player = move.opponent
        target_organ = move.opponent_organ
        if not target_organ:
            return True

        return target_organ.state_handler.on_virus_play(
            virus_card=self,
            target_organ=target_organ,
            target_player=target_player,
            owner=owner,
            game_state=game_state
        )

    def prepare_moves(self, player, game_state) -> List[Move]:
        chosen_opponent = player.decide_opponent(game_state, self)
        if self.color == CardColor.WILD or any(organ.color == CardColor.WILD for organ in chosen_opponent.body):
            chosen_color = player.decide_organ_color(game_state, opponent_body=chosen_opponent.body)
        else:
            chosen_color = player.get_organ_by_color(self.color)
        chosen_organ = chosen_opponent.get_organ_by_color(chosen_color)

        if chosen_organ:
            if not (chosen_organ.color == CardColor.WILD and self.color in chosen_opponent.organ_colors):  # cannot turn wild organ into a color that is already in opponent's body
                return [Move(opponent=chosen_opponent, opponent_organ=chosen_organ)]

    def can_be_played(self, game_state: 'GameState', owner: 'Player'):
        opponents = game_state.get_opponents(owner)
        for opponent in opponents:
            for organ in opponent.body:
                if organ.state != OrganState.IMMUNISED:
                    if self.color == CardColor.WILD:
                        return True
                    if organ.color in [self.color, CardColor.WILD]:
                        return True


class Organ(ColoredCard):
    def __init__(self, color):
        self.name = f"{color} {CardType.ORGAN}"
        self.original_color = color
        self.state_handler = HealthyStateHandler()
        self.viruses = []
        self.medicines = []
        super().__init__(CardType.ORGAN, color)

    @property
    def state(self):
        return self.state_handler.state

    def __repr__(self):
        return f"{self.name}{' ('+self.color.upper()+')' if self.color != self.original_color else ''} ({'+' * len(self.medicines)}{'-' * len(self.viruses)})"

    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool:
        if any(organ.color == self.color for organ in owner.body):
            return True
        owner.add_card_to_body(self)

    def can_be_played(self, game_state: 'GameState', owner: 'Player'):
        organ_colors = [organ.color for organ in owner.body]
        if self.color not in organ_colors:
            return True

    def discard(self, game_state):
        while self.viruses:
            virus = self.remove_virus()
            game_state.add_card_to_discard_pile(virus)
        while self.medicines:
            medicine = self.remove_medicine()
            game_state.add_card_to_discard_pile(medicine)

        game_state.add_card_to_discard_pile(self)

    def add_virus(self, virus_card):
        self.viruses.append(virus_card)
        self.state_handler.apply_virus(self, virus_card)

    def remove_virus(self):
        virus = self.viruses.pop()
        self.state_handler.remove_virus(self, virus)
        return virus

    def add_medicine(self, medicine):
        self.medicines.append(medicine)
        self.state_handler.apply_medicine(self, medicine)

    def remove_medicine(self):
        medicine = self.medicines.pop()
        self.state_handler.remove_medicine(self, medicine)
        return medicine

    def prepare_moves(self, player, game_state) -> List[Move]:
        if self.color not in player.organ_colors:
            return [Move()]

    def reset_wild_card(self):
        if self.original_color == CardColor.WILD:
            self.color = CardColor.WILD


class TreatmentCard(Card, ABC):
    def __init__(self, name):
        super().__init__(name, CardType.TREATMENT)


class OrganThief(TreatmentCard):
    def __init__(self):
        super().__init__(TreatmentName.ORGAN_THIEF)

    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool:
        target = move.opponent
        target_organ = move.opponent_organ
        target.remove_organ_from_body(target_organ)
        owner.add_card_to_body(target_organ)
        game_state.add_card_to_discard_pile(self)

    def can_be_played(self, game_state: 'GameState', owner: 'Player') -> bool:
        opponents = game_state.get_opponents(owner)
        for opponent in opponents:
            owner_organ_colors = [organ.color for organ in owner.body]
            if any(organ.color not in owner_organ_colors for organ in opponent.body):
                return True

    def prepare_moves(self, player, game_state):
        chosen_opponent = player.decide_opponent(game_state, self)
        chosen_color = player.decide_organ_color(game_state, opponent_body=chosen_opponent.body)
        chosen_organ = chosen_opponent.get_organ_by_color(chosen_color)
        if chosen_organ and chosen_organ.state < OrganState.IMMUNISED and chosen_organ.color not in player.organ_colors:
            return [Move(opponent=chosen_opponent, opponent_organ=chosen_organ)]


class Contagion(TreatmentCard):
    def __init__(self):
        super().__init__(TreatmentName.CONTAGION)

    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool:
        infected_organ = move.player_organ
        virus = infected_organ.viruses[0]
        is_error = virus.play(game_state, owner, move)
        if not is_error:
            infected_organ.remove_virus()
        else:
            return True
        game_state.add_card_to_discard_pile(self)

    def can_be_played(self, game_state: 'GameState', owner: 'Player') -> bool:
        infected_organs = [organ for organ in owner.body if organ.state == OrganState.INFECTED]
        for organ in infected_organs:
            for virus in organ.viruses:
                if virus.can_be_played(game_state, owner):
                    return True

    def prepare_moves(self, player, game_state):
        for infected_player_organ in player.body:
            for virus in infected_player_organ.viruses:
                chosen_opponent = player.decide_opponent(game_state, self)
                if virus.color == CardColor.WILD:
                    chosen_color = player.decide_organ_color(game_state, opponent_body=chosen_opponent.body)
                else:
                    chosen_color = virus.color
                chosen_organ = chosen_opponent.get_organ_by_color(chosen_color)
                if chosen_organ:
                    return [Move(opponent=chosen_opponent, player_organ=infected_player_organ,
                                 opponent_organ=chosen_organ)]


class Transplant(TreatmentCard):
    def __init__(self):
        super().__init__(TreatmentName.TRANSPLANT)

    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool:
        target = move.opponent
        stolen_organ = move.opponent_organ
        given_organ = move.player_organ
        target.remove_organ_from_body(stolen_organ)
        owner.add_card_to_body(stolen_organ)
        owner.remove_organ_from_body(given_organ)
        target.add_card_to_body(given_organ)
        game_state.add_card_to_discard_pile(self)

    def can_be_played(self, game_state: 'GameState', owner: 'Player') -> bool:
        if not any(organ for organ in owner.body if organ.state != OrganState.IMMUNISED):
            return False

        opponents = game_state.get_opponents(owner)
        for opponent in opponents:
            if any(organ for organ in opponent.body if organ.state != OrganState.IMMUNISED):
                return True

    def prepare_moves(self, player, game_state):
        chosen_opponent = player.decide_opponent(game_state, self)
        chosen_player_color = player.decide_organ_color(game_state)
        chosen_opponent_color = player.decide_organ_color(game_state, opponent_body=chosen_opponent.body)
        chosen_player_organ = player.get_organ_by_color(chosen_player_color)
        chosen_opponent_organ = chosen_opponent.get_organ_by_color(chosen_opponent_color)
        # TODO: move the validation logic to play() or separate CardValidator class
        if chosen_player_organ and chosen_opponent_organ and chosen_player_organ.state < OrganState.IMMUNISED and chosen_opponent_organ.state < OrganState.IMMUNISED and chosen_opponent_organ.color not in player.organ_colors and chosen_player_organ.color not in chosen_opponent.organ_colors:
            return [Move(opponent=chosen_opponent, player_organ=chosen_player_organ,
                         opponent_organ=chosen_opponent_organ)]


class MedicalError(TreatmentCard):
    def __init__(self):
        super().__init__(TreatmentName.MEDICAL_ERROR)

    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool:
        target = move.opponent
        owner.body, target.body = target.body, owner.body
        game_state.add_card_to_discard_pile(self)

    def can_be_played(self, game_state: 'GameState', owner: 'Player') -> bool:
        opponents = game_state.get_opponents(owner)
        if any(opponent.body for opponent in opponents):
            return True

    def prepare_moves(self, player, game_state):
        chosen_opponent = player.decide_opponent(game_state, self)
        if chosen_opponent:
            return [Move(opponent=chosen_opponent)]


class LatexGlove(TreatmentCard):
    def __init__(self):
        super().__init__(TreatmentName.LATEX_GLOVE)

    def play(self, game_state: 'GameState', owner: 'Player', move: 'Move') -> bool:
        opponents = game_state.get_opponents(owner)
        for opponent in opponents:
            while opponent.hand:
                card = opponent.hand.pop()
                game_state.add_card_to_discard_pile(card)
        game_state.add_card_to_discard_pile(self)

    def can_be_played(self, game_state: 'GameState', owner: 'Player') -> bool:
        return True

    def prepare_moves(self, player, game_state):
        return [Move()]
