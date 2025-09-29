import unittest
from enums import CardType, TreatmentName, CardColor, OrganState
from players.strategy_based_ai import StrategyBasedAIPlayer
from game.game_state import GameState
from models.cards import Card, Organ


class TestRuleBasedAIPlayer(unittest.TestCase):
    def setUp(self):

        self.player = StrategyBasedAIPlayer("AI Player")
        self.opponent = StrategyBasedAIPlayer("Opponent")
        players = [self.player, self.opponent]
        self.game_state = GameState(players)

    def _add_organs(self, player, colors, state=OrganState.HEALTHY):
        """Helper to add multiple organs to a player"""
        for color in colors:
            player.add_organ_to_body(Organ(color, state))

    def _add_card(self, player, card_type, name=None, color=CardColor.RED):
        """Helper to add card to player's hand"""
        card = Card(card_type, color=color, name=name)
        player.add_card_to_hand(card)
        return card

    def test_winning_move_with_organ_card(self):
        # Player has 3 healthy organs and needs a 4th
        self._add_organs(self.player, [CardColor.RED, CardColor.BLUE, CardColor.GREEN])
        organ_card = self._add_card(self.player, CardType.ORGAN, color=CardColor.YELLOW)

        result = self.player.prepare_moves(self.game_state)
        self.assertEqual(result[0], organ_card)
        self.assertEqual(len(result[1]), 1)

    def test_medical_error_play(self):
        # Setup opponent with better organs
        self._add_organs(self.opponent, [CardColor.RED, CardColor.BLUE], OrganState.IMMUNISED)
        self._add_organs(self.player, [CardColor.RED, CardColor.BLUE], OrganState.INFECTED)

        med_error = self._add_card(self.player, CardType.TREATMENT, TreatmentName.MEDICAL_ERROR)

        result = self.player.prepare_moves(self.game_state)
        self.assertEqual(result[0], med_error)
        self.assertEqual(result[1][0].opponent, self.opponent)

    def test_organ_thief_priority(self):
        # Player needs YELLOW organ
        self._add_organs(self.player, [CardColor.RED, CardColor.BLUE, CardColor.GREEN])
        self._add_organs(self.opponent, [CardColor.YELLOW])

        thief_card = self._add_card(self.player, CardType.TREATMENT, TreatmentName.ORGAN_THIEF)

        result = self.player.prepare_moves(self.game_state)
        self.assertEqual(result[0], thief_card)
        self.assertEqual(result[1][0].opponent_organ.color, CardColor.YELLOW)

    def test_discard_unplayable_cards(self):
        # Add duplicate organ card (unplayable)
        self._add_organs(self.player, [CardColor.RED])
        self._add_card(self.player, CardType.ORGAN, color=CardColor.RED)

        discard_indices = self.player.decide_cards_to_discard_indices(self.game_state)
        self.assertEqual(len(discard_indices), 1)
        self.assertEqual(self.player.hand[discard_indices[0]].type, CardType.ORGAN)

    def test_latex_glove_fallback(self):
        # Only has latex glove
        glove = self._add_card(self.player, CardType.TREATMENT, TreatmentName.LATEX_GLOVE)

        result = self.player.prepare_moves(self.game_state)
        self.assertEqual(result[0], glove)
        self.assertEqual(len(result[1]), 1)

    def test_medicine_priority(self):
        # Player has infected organ and medicine
        self._add_organs(self.player, [CardColor.RED], OrganState.INFECTED)
        medicine = self._add_card(self.player, CardType.MEDICINE, color=CardColor.RED)

        result = self.player.prepare_moves(self.game_state)
        self.assertEqual(result[0], medicine)
        self.assertEqual(result[1][0].player_organ.color, CardColor.RED)

    def test_virus_attack_priority(self):
        # Setup vulnerable opponent organ
        self._add_organs(self.opponent, [CardColor.BLUE])
        virus = self._add_card(self.player, CardType.VIRUS, color=CardColor.BLUE)

        result = self.player.prepare_moves(self.game_state)
        self.assertEqual(result[0], virus)
        self.assertEqual(result[1][0].opponent_organ.color, CardColor.BLUE)


if __name__ == '__main__':
    unittest.main()
