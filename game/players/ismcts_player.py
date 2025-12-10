import random
from typing import List, Optional, Tuple

from game.enums import Action, CardColor
from game.state import GameState
from game.models.cards import Card
from game.models.move import Move
from game.players.base_player import BasePlayer


class ISMCTSNode:
    def __init__(self, state: GameState, parent: Optional['ISMCTSNode'] = None, move: Optional[Tuple[int, List[Move]]] = None):
        self.state = state
        self.parent = parent
        self.move = move  # (card_index, moves)
        self.children: List['ISMCTSNode'] = []
        self.visits = 0
        self.wins = 0

    def is_fully_expanded(self):
        return len(self.children) > 0

    def uct_score(self, total_simulations: int, c: float = 1.41) -> float:
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + c * ((total_simulations ** 0.5) / (1 + self.visits))


class ISMCTSPlayer(BasePlayer):
    def __init__(self, name: str, iterations: int = 1000):
        super().__init__(name)
        self.iterations = iterations

    def decide_action(self, game_state: GameState) -> Action:
        if not any(card.can_be_played(game_state, self) for card in self.hand):
            return Action.DISCARD
        return Action.PLAY

    def decide_card_to_play_index(self, game_state: GameState) -> int:
        best_move = self._ismcts_search(game_state)
        if best_move[0]:
            return best_move[0]
        # fallback random playable
        playable = [i for i, card in enumerate(self.hand) if card.can_be_played(game_state, self)]
        return random.choice(playable) if playable else 0

    def decide_opponent(self, game_state: GameState, card: Card) -> BasePlayer:
        opponents = game_state.get_opponents(self)
        return random.choice(opponents)

    def decide_organ_color(self, game_state: GameState, opponent_body=None) -> CardColor:
        return random.choice(list(CardColor))

    def decide_cards_to_discard_indices(self, game_state: GameState) -> List[int]:
        num_cards = random.randint(1, len(self.hand))
        return random.sample(range(len(self.hand)), num_cards)

    def _ismcts_search(self, root_state: GameState) -> Optional[Tuple[int, List[Move]]]:
        root = ISMCTSNode(self._determinize(root_state))
        for _ in range(self.iterations):
            node = root
            # Selection
            while node.is_fully_expanded() and node.children:
                total_visits = sum(ch.visits for ch in node.children)
                node = max(node.children, key=lambda n: n.uct_score(total_visits))
            # Expansion
            if not node.is_fully_expanded():
                expanded = self._expand(node)
                if expanded:
                    node = expanded
            # Simulation & Backprop
            win = self._simulate(node.state)
            self._backpropagate(node, win)
        if not root.children:
            return None
        best = max(root.children, key=lambda n: n.visits)
        return best.move

    def _expand(self, node: ISMCTSNode) -> Optional[ISMCTSNode]:
        state = node.state
        current = state.get_current_player()
        moves: List[Tuple[Optional[int], List[Move]]] = []
        # playable card moves
        for idx, card in enumerate(current.hand):
            if card.can_be_played(state, current):
                prepared = card.prepare_moves(current, state) or []
                if prepared:
                    moves.append((idx, prepared))
        # if no moves, discard
        if not moves:
            moves.append((None, []))
        # filter tried
        tried = [child.move for child in node.children]
        options = [m for m in moves if m not in tried]
        if not options:
            return None
        move = random.choice(options)
        next_state = self._apply_move(state, move)
        child = ISMCTSNode(state=next_state, parent=node, move=move)
        node.children.append(child)
        return child

    def _simulate(self, state: GameState) -> bool:
        sim = state.clone()
        max_simulation_turns = 1000
        turn_count = 0
        
        while not sim.is_game_over() and turn_count < max_simulation_turns:
            player = sim.get_current_player()
            sim.complete_hand(player)

            # check win condition for current player
            if sim.check_win_condition(player):
                sim.winner = player
                break
            
            # gather playable with valid moves
            options: List[Tuple[Card, List[Move]]] = []
            for card in list(player.hand):
                if card.can_be_played(sim, player):
                    prepared = card.prepare_moves(player, sim) or []
                    if prepared:
                        options.append((card, prepared))
            if options:
                card, prepared_moves = random.choice(options)
                move = random.choice(prepared_moves)
                card.play(sim, player, move)
                player.hand.remove(card)
            else:
                # discard random card
                if player.hand:
                    card = random.choice(player.hand)
                    player.hand.remove(card)
                    sim.add_card_to_discard_pile(card)
            
            sim.next_player()
            turn_count += 1
        
        winner = sim.get_winner()
        return winner is not None and winner.name == self.name

    def _backpropagate(self, node: ISMCTSNode, win: bool) -> None:
        while node:
            node.visits += 1
            if win:
                node.wins += 1
            node = node.parent

    def _determinize(self, state: GameState) -> GameState:
        det = state.clone()
        # TODO: proper dealing of hidden cards
        return det

    def _apply_move(self, state: GameState, move: Tuple[Optional[int], List[Move]]) -> GameState:
        new_state = state.clone()
        player = new_state.get_current_player()
        card_index, original_moves = move

        # Create moves with updated references
        def resolve_organ(source_body, original_organ):
            for organ in source_body:
                if organ.name == original_organ.name:
                    return organ
            return None

        updated_moves = []
        for m in original_moves:
            new_move = Move()
            if m.player_organ:
                new_move.player_organ = resolve_organ(player.body, m.player_organ)
            if m.opponent:
                new_move.opponent = new_state.get_player_by_name(m.opponent.name)
                if m.opponent_organ:
                    new_move.opponent_organ = resolve_organ(new_move.opponent.body, m.opponent_organ)
            updated_moves.append(new_move)

        if card_index is None:
            if player.hand:
                card = player.hand.pop(0)
                new_state.add_card_to_discard_pile(card)
        else:
            card = player.hand[card_index]
            for m in updated_moves:
                card.play(new_state, player, m)
            player.hand.remove(card)

        new_state.next_player()
        return new_state
