import unittest

from game_config import GameConfig
from enums import PlayerType, OrganState, CardColor, CardType, TreatmentName
from cards import Organ, Medicine, Virus, Treatment
from game import VirusGame

# test cannot add two organs of the same color

class TestVirusGame(unittest.TestCase):
    def setUp(self):
        # Set up a game for testing
        config = GameConfig()
        config.add_player(PlayerType.RANDOM, "Player1")
        config.add_player(PlayerType.RANDOM, "Player2")
        self.game = VirusGame(config)

    def test_initial_setup(self):
        # Check if the game is initialized correctly
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(len(self.game.deck.cards), 68)
        self.assertEqual(len(self.game.players[0].hand), 0)
        self.assertEqual(len(self.game.players[1].hand), 0)

    def test_complete_hand(self):
        # Test if hands are completed correctly
        for player in self.game.players:
            self.game.complete_hand(player)
            self.assertEqual(len(player.hand), 3)

    def test_check_win_condition_four_organs(self):
        # Test the win condition
        player = self.game.players[0]
        # Add 4 healthy organs to the player's body (simulating a win)
        player.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.BLUE), Organ(CardColor.YELLOW)]
        self.assertTrue(self.game.check_win_condition(player))

    def test_check_win_condition_five_organs(self):
        # Test the win condition
        player = self.game.players[0]
        # Add 4 healthy organs to the player's body (simulating a win)
        player.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.BLUE), Organ(CardColor.YELLOW), Organ(CardColor.WILD)]
        self.assertTrue(self.game.check_win_condition(player))

    def test_check_win_condition_four_organs_one_wild(self):
        # Test the win condition
        player = self.game.players[0]
        # Add 4 healthy organs to the player's body (simulating a win)
        player.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.YELLOW), Organ(CardColor.WILD)]
        self.assertTrue(self.game.check_win_condition(player))

    def test_check_win_condition_four_organs_one_infected(self):
        # Test the win condition
        player = self.game.players[0]
        # Add 4 healthy organs to the player's body (simulating a win)
        player.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.YELLOW), Organ(CardColor.WILD)]
        player.body[0].add_virus(Virus(CardColor.RED))
        self.assertFalse(self.game.check_win_condition(player))

    def test_check_win_condition_five_organs_one_infected(self):
        # Test the win condition
        player = self.game.players[0]
        # Add 4 healthy organs to the player's body (simulating a win)
        player.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.YELLOW), Organ(CardColor.WILD), Organ(CardColor.BLUE)]
        player.body[0].add_virus(Virus(CardColor.RED))
        self.assertTrue(self.game.check_win_condition(player))

    def test_draw_card(self):
        # Test drawing a card from the deck
        initial_deck_size = len(self.game.deck.cards)
        card = self.game.deck.draw_card()
        self.assertEqual(len(self.game.deck.cards), initial_deck_size - 1)
        self.assertIsNotNone(card)

    def test_discard_card(self):
        # Test discarding a card
        card = self.game.deck.draw_card()
        self.game.add_to_discard_pile(card)
        self.assertIn(card, self.game.deck.discard_pile)

    def test_play_medicine_on_healthy_organ(self):
        # Test playing a medicine card on a healthy organ
        player = self.game.players[0]
        # Add a healthy organ and a medicine card to the player's hand
        player.add_card_to_hand(Organ(CardColor.RED))
        player.add_card_to_hand(Medicine(CardColor.RED))
        player.play_card(self.game, 0)  # Play the organ card
        player.play_card(self.game, 0)  # Play the medicine card
        organ = player.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.VACCINATED)

    def test_play_medicine_on_vaccinated_organ(self):
        # Test playing a medicine card on a healthy organ
        player = self.game.players[0]
        # Add a healthy organ and a medicine card to the player's hand
        player.add_card_to_hand(Organ(CardColor.RED))
        player.add_card_to_hand(Medicine(CardColor.RED))
        player.add_card_to_hand(Medicine(CardColor.RED))
        player.play_card(self.game, 0)  # Play the organ card
        player.play_card(self.game, 0)  # Play the medicine card
        player.play_card(self.game, 0)  # Play the medicine card
        organ = player.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.IMMUNISED)

    def test_play_medicine_on_immunised_organ(self):
        # Test playing a medicine card on a healthy organ
        player = self.game.players[0]
        # Add a healthy organ and a medicine card to the player's hand
        player.add_card_to_hand(Organ(CardColor.RED))
        player.play_card(self.game, 0)  # Play the organ card
        player.add_card_to_hand(Medicine(CardColor.RED))
        player.add_card_to_hand(Medicine(CardColor.RED))
        player.add_card_to_hand(Medicine(CardColor.RED))
        player.play_card(self.game, 0)  # Play the medicine card
        player.play_card(self.game, 0)  # Play the medicine card
        is_error = player.play_card(self.game, 0)  # Play the medicine card (should return error boolean)
        self.assertTrue(is_error)

    def test_play_virus_on_healthy_organ(self):
        # Test playing a virus card on a healthy organ
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add a healthy organ to player1's hand and a virus card to player2's hand
        player1.add_card_to_hand(Organ(CardColor.RED))
        player2.add_card_to_hand(Virus(CardColor.RED))
        player1.play_card(self.game, 0)  # Player1 plays the organ card
        player2.play_card(self.game, 0)  # Player2 plays the virus card
        organ = player1.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.INFECTED)

    def test_play_virus_on_infected_organ(self):
        # Test playing a virus card on a healthy organ
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add a healthy organ to player1's hand and virus cards to player2's hand
        player1.add_card_to_hand(Organ(CardColor.RED))
        player2.add_card_to_hand(Virus(CardColor.RED))
        player2.add_card_to_hand(Virus(CardColor.RED))
        player1.play_card(self.game, 0)  # Player1 plays the organ card
        player2.play_card(self.game, 0)  # Player2 plays the virus card
        player2.play_card(self.game, 0)  # Player2 plays the virus card
        self.assertFalse(self.game.players[0].body)
        self.assertEqual(len(self.game.deck.discard_pile), 3)

    def test_play_virus_on_vaccinated_organ(self):
        # Test playing a virus card on a healthy organ
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add a healthy organ to player1's hand and a virus card to player2's hand
        player1.add_card_to_hand(Organ(CardColor.RED))
        player1.add_card_to_hand(Medicine(CardColor.RED))
        player2.add_card_to_hand(Virus(CardColor.RED))
        player1.play_card(self.game, 0)  # Player1 plays the organ card
        player1.play_card(self.game, 0)  # Player1 plays the medicine card
        player2.play_card(self.game, 0)  # Player2 plays the virus card
        organ = player1.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.HEALTHY)
        self.assertFalse(organ.medicines)
        self.assertFalse(organ.viruses)
        self.assertEqual(len(self.game.deck.discard_pile), 2)

    def test_play_virus_on_immunised_organ(self):
        # Test playing a virus card on a healthy organ
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add a healthy organ to player1's hand and a virus card to player2's hand
        player1.add_card_to_hand(Organ(CardColor.RED))
        player1.add_card_to_hand(Medicine(CardColor.RED))
        player1.add_card_to_hand(Medicine(CardColor.RED))
        player2.add_card_to_hand(Virus(CardColor.RED))
        player1.play_card(self.game, 0)  # Player1 plays the organ card
        player1.play_card(self.game, 0)  # Player1 plays the medicine card
        player1.play_card(self.game, 0)  # Player1 plays the medicine card
        is_error = player2.play_card(self.game, 0)  # Player2 plays the virus card
        organ = player1.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.IMMUNISED)
        self.assertTrue(is_error)

    def test_play_contagion_treatment(self):
        # Test playing the Contagion treatment card
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add infected organs to both players' bodies
        player1.add_card_to_body(Organ(CardColor.RED))
        player1.add_card_to_body(Organ(CardColor.BLUE))
        player2.add_card_to_body(Organ(CardColor.RED))
        player2.add_card_to_body(Organ(CardColor.BLUE))
        player1_red_organ = player1.get_organ_by_color(CardColor.RED)
        player1_blue_organ = player1.get_organ_by_color(CardColor.BLUE)
        player2_red_organ = player2.get_organ_by_color(CardColor.RED)
        player2_blue_organ = player2.get_organ_by_color(CardColor.BLUE)
        player1_red_organ.add_virus(Virus(CardColor.RED))
        player1_blue_organ.add_virus(Virus(CardColor.BLUE))
        player1.add_card_to_hand(Treatment(TreatmentName.CONTAGION))
        player1.play_card(self.game, -1)  # Player1 plays the Contagion card
        # Check if the virus spread to player2's organ
        self.assertEqual(player2_red_organ.state, OrganState.INFECTED)
        self.assertEqual(player2_blue_organ.state, OrganState.INFECTED)

    def test_play_organ_thief_treatment(self):
        # Test playing the Organ Thief treatment card
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add a healthy organ to player1's body and an Organ Thief card to player2's hand
        player1.add_card_to_body(Organ(CardColor.RED))
        player2.add_card_to_hand(Treatment(TreatmentName.ORGAN_THIEF))
        player2.play_card(self.game, 0)  # Player2 plays the Organ Thief card
        # Check if the organ was stolen from player1
        self.assertEqual(len(player1.body), 0)
        self.assertEqual(len(player2.body), 1)

    def test_play_transplant_treatment(self):
        # Test playing the Transplant treatment card
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add healthy organs of different colors to both players' bodies
        player1.add_card_to_body(Organ(CardColor.RED))
        player2.add_card_to_body(Organ(CardColor.BLUE))
        player2.add_card_to_hand(Treatment(TreatmentName.TRANSPLANT))
        player2.play_card(self.game, -1)  # Player2 plays the Transplant card
        # Check if the organs were swapped
        self.assertEqual(player1.body[0].color, CardColor.BLUE)
        self.assertEqual(player2.body[0].color, CardColor.RED)

    def test_play_latex_glove_treatment(self):
        # Test playing the Latex Glove treatment card
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add cards to player1's hand and a Latex Glove card to player2's hand
        player1.add_card_to_hand(Organ(CardColor.RED))
        player1.add_card_to_hand(Virus(CardColor.BLUE))
        player2.add_card_to_hand(Treatment(TreatmentName.LATEX_GLOVE))
        player2.play_card(self.game, 0)  # Player2 plays the Latex Glove card
        # Check if player1's hand is empty
        self.assertEqual(len(player1.hand), 0)

    def test_play_medical_error_treatment(self):
        # Test playing the Medical Error treatment card
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        # Add different organs to both players' bodies
        player1.add_card_to_body(Organ(CardColor.RED))
        player1.add_card_to_body(Organ(CardColor.BLUE))
        player1.add_card_to_body(Organ(CardColor.YELLOW))
        player2.add_card_to_body(Organ(CardColor.RED))
        player2.add_card_to_hand(Treatment(TreatmentName.MEDICAL_ERROR))
        player2.play_card(self.game, -1)  # Player2 plays the Medical Error card
        # Check if the organs were swapped
        self.assertEqual(len(player1.body), 1)
        self.assertEqual(len(player2.body), 3)

    def test_player_draw_card(self):
        # Test player drawing a card from the deck
        player = self.game.players[0]
        initial_deck_size = len(self.game.deck.cards)
        player.draw_card(self.game.deck)
        self.assertEqual(len(self.game.deck.cards), initial_deck_size - 1)
        self.assertEqual(len(player.hand), 1)

    def test_player_discard_card(self):
        # Test player discarding a card
        player = self.game.players[0]
        card = self.game.deck.draw_card()
        player.add_card_to_hand(card)
        player.discard_card(self.game.deck, 0)
        self.assertIn(card, self.game.deck.discard_pile)
        self.assertEqual(len(player.hand), 0)

    def test_player_play_organ(self):
        # Test player playing an organ card
        player = self.game.players[0]
        card = Organ(CardColor.RED)
        player.add_card_to_hand(card)
        player.play_card(self.game, 0)
        self.assertIn(card, player.body)
        self.assertEqual(len(player.hand), 0)

    def test_player_cannot_play_if_no_cards(self):
        # Test that player cannot play a card that is not in their hand
        player1 = self.game.players[0]
        is_error = player1.play_card(self.game, 0) # Expect the is_error to return True to block the move
        self.assertTrue(is_error)

if __name__ == '__main__':
    unittest.main()
