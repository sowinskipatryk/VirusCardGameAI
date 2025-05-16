import unittest

from players import PlayerFactory
from enums import PlayerType, OrganState, CardColor
from models.cards import Organ, Medicine, Virus, Contagion, MedicalError, Transplant, OrganThief, LatexGlove, Move
from game.game_manager import GameManager


class TestGameManager(unittest.TestCase):
    def setUp(self):
        # Set up a game for testing
        config = PlayerFactory()
        self.player1 = config.add_player(PlayerType.RANDOM, "Player1")
        self.player2 = config.add_player(PlayerType.RANDOM, "Player2")
        self.game_manager = GameManager(config)
        self.state = self.game_manager.state

    def test_initial_setup(self):
        # Check if the game is initialized correctly
        self.assertEqual(len(self.state.players), 2)
        self.assertEqual(len(self.state.deck.cards), 68)
        self.assertEqual(len(self.state.players[0].hand), 0)
        self.assertEqual(len(self.state.players[1].hand), 0)

    def test_complete_hand(self):
        # Test if hands are completed correctly
        for player in self.state.players:
            self.state.complete_hand(player)
            self.assertEqual(len(player.hand), 3)

    def test_check_win_condition_four_organs(self):
        # Test the win condition
        # Add 4 healthy organs to the player's body (simulating a win)
        self.player1.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.BLUE), Organ(CardColor.YELLOW)]
        self.assertTrue(self.game_manager.check_win_condition(self.player1))

    def test_check_win_condition_five_organs(self):
        # Test the win condition
        # Add 4 healthy organs to the player's body (simulating a win)
        self.player1.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.BLUE), Organ(CardColor.YELLOW), Organ(CardColor.WILD)]
        self.assertTrue(self.game_manager.check_win_condition(self.player1))

    def test_check_win_condition_four_organs_one_wild(self):
        # Test the win condition
        # Add 4 healthy organs to the player's body (simulating a win)
        self.player1.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.YELLOW), Organ(CardColor.WILD)]
        self.assertTrue(self.game_manager.check_win_condition(self.player1))

    def test_check_win_condition_four_organs_one_infected(self):
        # Test the win condition
        # Add 4 healthy organs to the player's body (simulating a win)
        self.player1.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.YELLOW), Organ(CardColor.WILD)]
        self.player1.body[0].add_virus(Virus(CardColor.RED))
        self.assertFalse(self.game_manager.check_win_condition(self.player1))

    def test_check_win_condition_four_organs_mixed_states(self):
        # Test the win condition
        # Add 4 healthy organs to the player's body (simulating a win)
        self.player1.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.YELLOW), Organ(CardColor.WILD)]
        self.player1.body[0].add_medicine(Medicine(CardColor.RED))
        self.player1.body[1].add_medicine(Medicine(CardColor.GREEN))
        self.player1.body[1].add_medicine(Medicine(CardColor.GREEN))
        self.assertTrue(self.game_manager.check_win_condition(self.player1))

    def test_check_win_condition_five_organs_one_infected(self):
        # Test the win condition
        # Add 4 healthy organs to the player's body (simulating a win)
        self.player1.body = [Organ(CardColor.RED), Organ(CardColor.GREEN), Organ(CardColor.YELLOW), Organ(CardColor.WILD), Organ(CardColor.BLUE)]
        self.player1.body[0].add_virus(Virus(CardColor.RED))
        self.assertTrue(self.game_manager.check_win_condition(self.player1))

    def test_draw_card(self):
        # Test drawing a card from the deck
        initial_deck_size = len(self.state.deck.cards)
        card = self.state.deck.draw_card()
        self.assertEqual(len(self.state.deck.cards), initial_deck_size - 1)
        self.assertIsNotNone(card)

    def test_discard_card(self):
        # Test discarding a card
        card = self.state.deck.draw_card()
        self.state.add_card_to_discard_pile(card)
        self.assertIn(card, self.state.deck.discard_pile)

    def test_play_medicine_on_healthy_organ(self):
        # Test playing a medicine card on a healthy organ
        # Add a healthy organ and a medicine card to the player's hand
        red_organ = Organ(CardColor.RED)
        red_medicine = Medicine(CardColor.RED)
        self.player1.add_card_to_hand(red_organ)
        self.player1.add_card_to_hand(red_medicine)
        moves = [Move()]
        self.player1.play_card(self.state, red_organ, moves)  # Play the organ card
        moves = [Move(player_organ=red_organ)]
        self.player1.play_card(self.state, red_medicine, moves)  # Play the medicine card
        organ = self.player1.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.VACCINATED)

    def test_play_medicine_on_vaccinated_organ(self):
        # Test playing a medicine card on a healthy organ
        # Add a healthy organ and a medicine card to the player's hand
        cards = [Organ(CardColor.RED), Medicine(CardColor.RED), Medicine(CardColor.RED)]
        self.player1.add_card_to_hand(cards[0])
        self.player1.add_card_to_hand(cards[1])
        self.player1.add_card_to_hand(cards[2])
        moves = [Move()]
        self.player1.play_card(self.player1, cards[0], moves)  # Play the organ card
        moves = [Move(player_organ=cards[0])]
        self.player1.play_card(self.player1, cards[1], moves)  # Play the medicine card
        moves = [Move(player_organ=cards[0])]
        self.player1.play_card(self.player1, cards[2], moves)  # Play the medicine card
        organ = self.player1.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.IMMUNISED)

    def test_play_colored_medicine_on_wild_organ(self):
        # Test playing a colored medicine card on a wild organ
        # Add a healthy organ and a medicine card to the player's hand
        wild_organ = Organ(CardColor.WILD)
        red_medicine = Medicine(CardColor.RED)
        self.player1.add_card_to_hand(wild_organ)
        self.player1.add_card_to_hand(red_medicine)
        moves = [Move()]
        self.player1.play_card(self.player1, wild_organ, moves)  # Play the organ card
        moves = [Move(player_organ=wild_organ)]
        self.player1.play_card(self.player1, red_medicine, moves)  # Play the medicine card
        self.assertEqual(self.player1.body[0].state, OrganState.VACCINATED)
        self.assertEqual(self.player1.body[0].color, CardColor.RED)

    def test_play_wild_medicine_on_wild_organ(self):
        # Test playing a wild medicine card on a wild organ
        # Add a healthy organ and a medicine card to the player's hand
        wild_organ = Organ(CardColor.WILD)
        wild_medicine = Medicine(CardColor.WILD)
        self.player1.add_card_to_hand(wild_organ)
        self.player1.add_card_to_hand(wild_medicine)
        moves = [Move()]
        self.player1.play_card(self.player1, wild_organ, moves)  # Play the organ card
        moves = [Move(player_organ=wild_organ)]
        self.player1.play_card(self.player1, wild_medicine, moves)  # Play the medicine card
        self.assertEqual(self.player1.body[0].state, OrganState.VACCINATED)

    def test_play_medicine_on_immunised_organ(self):
        # Test playing a medicine card on a healthy organ
        # Add a healthy organ and a medicine card to the player's hand
        cards = [Organ(CardColor.RED), Medicine(CardColor.RED), Medicine(CardColor.RED), Medicine(CardColor.RED)]
        self.player1.add_card_to_hand(cards[0])
        moves = [Move()]
        self.player1.play_card(self.player1, cards[0], moves)  # Play the organ card
        self.player1.add_card_to_hand(cards[1])
        self.player1.add_card_to_hand(cards[2])
        self.player1.add_card_to_hand(cards[3])
        moves = [Move(player_organ=cards[0])]
        self.player1.play_card(self.state, cards[1], moves)  # Play the medicine card
        moves = [Move(player_organ=cards[0])]
        self.player1.play_card(self.state, cards[2], moves)  # Play the medicine card
        moves = [Move(player_organ=cards[0])]
        num_successful_moves = self.player1.play_card(self.state, cards[3], moves)  # Play the medicine card (should return error boolean)
        self.assertEqual(num_successful_moves, 0)

    def test_play_virus_on_healthy_organ(self):
        # Test playing a virus card on a healthy organ
        # Add a healthy organ to player1's hand and a virus card to player2's hand
        red_organ = Organ(CardColor.RED)
        red_virus = Virus(CardColor.RED)
        self.player1.add_card_to_hand(red_organ)
        self.player2.add_card_to_hand(red_virus)
        moves = [Move()]
        self.player1.play_card(self.state, red_organ, moves)
        moves = [Move(opponent=self.player1, opponent_organ=red_organ)]
        self.player2.play_card(self.state, red_virus, moves)
        organ = self.player1.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.INFECTED)

    def test_play_virus_on_infected_organ(self):
        # Test playing a virus card on a healthy organ
        # Add a healthy organ to player1's hand and virus cards to player2's hand
        cards = [Organ(CardColor.RED), Virus(CardColor.RED), Virus(CardColor.RED)]
        self.player1.add_card_to_hand(cards[0])
        self.player2.add_card_to_hand(cards[1])
        self.player2.add_card_to_hand(cards[2])
        moves = [Move()]
        self.player1.play_card(self.state, cards[0], moves)  # Player1 plays the organ card
        moves = [Move(opponent=self.player1, opponent_organ=cards[0])]
        self.player2.play_card(self.state, cards[1], moves)  # Player2 plays the virus card
        moves = [Move(opponent=self.player1, opponent_organ=cards[0])]
        self.player2.play_card(self.state, cards[2], moves)  # Player2 plays the virus card
        self.assertFalse(self.state.players[0].body)
        self.assertEqual(len(self.state.deck.discard_pile), 3)

    def test_play_virus_on_vaccinated_organ(self):
        # Test playing a virus card on a healthy organ
        # Add a healthy organ to player1's hand and a virus card to player2's hand
        cards = [Organ(CardColor.RED), Medicine(CardColor.RED), Virus(CardColor.RED)]
        self.player1.add_card_to_hand(cards[0])
        self.player1.add_card_to_hand(cards[1])
        self.player2.add_card_to_hand(cards[2])
        moves = [Move()]
        self.player1.play_card(self.state, cards[0], moves)  # Player1 plays the organ card
        moves = [Move(player_organ=cards[0])]
        self.player1.play_card(self.state, cards[1], moves)  # Player1 plays the medicine card
        moves = [Move(opponent=self.player1, opponent_organ=cards[0])]
        self.player2.play_card(self.state, cards[2], moves)  # Player2 plays the virus card
        organ = self.player1.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.HEALTHY)
        self.assertFalse(organ.medicines)
        self.assertFalse(organ.viruses)
        self.assertEqual(len(self.state.deck.discard_pile), 2)

    def test_play_colored_virus_on_wild_organ(self):
        # Test playing a colored virus card on a wild organ
        # Add a healthy organ and a virus card to the player's hand
        red_virus = Virus(CardColor.RED)
        wild_organ = Organ(CardColor.WILD)
        self.player1.add_card_to_hand(red_virus)
        self.player2.add_card_to_hand(wild_organ)
        moves = [Move()]
        self.player2.play_card(self.state, wild_organ, moves)  # Play the organ card
        moves = [Move(opponent=self.player1, opponent_organ=wild_organ)]
        self.player1.play_card(self.state, red_virus, moves)  # Play the virus card
        self.assertEqual(self.player2.body[0].state, OrganState.INFECTED)
        self.assertEqual(self.player2.body[0].color, CardColor.RED)

    def test_play_wild_virus_on_wild_organ(self):
        # Test playing a wild virus card on a wild organ
        # Add a healthy organ and a virus card to the player's hand
        wild_virus = Virus(CardColor.WILD)
        wild_organ = Organ(CardColor.WILD)
        self.player1.add_card_to_hand(wild_virus)
        self.player2.add_card_to_hand(wild_organ)
        moves = [Move()]
        self.player2.play_card(self.state, wild_organ, moves)  # Play the organ card
        moves = [Move(opponent=self.player1, opponent_organ=wild_organ)]
        self.player1.play_card(self.state, wild_virus, moves)  # Play the virus card
        self.assertEqual(self.player2.body[0].state, OrganState.INFECTED)

    def test_play_virus_on_immunised_organ(self):
        # Test playing a virus card on a healthy organ
        # Add a healthy organ to player1's hand and a virus card to player2's hand
        cards = [Organ(CardColor.RED), Medicine(CardColor.RED), Medicine(CardColor.RED), Virus(CardColor.RED)]
        self.player1.add_card_to_hand(cards[0])
        self.player1.add_card_to_hand(cards[1])
        self.player1.add_card_to_hand(cards[2])
        self.player2.add_card_to_hand(cards[3])
        moves = [Move()]
        self.player1.play_card(self.state, cards[0], moves)  # Player1 plays the organ card
        moves = [Move(player_organ=cards[0])]
        self.player1.play_card(self.state, cards[1], moves)  # Player1 plays the medicine card
        moves = [Move(player_organ=cards[0])]
        self.player1.play_card(self.state, cards[2], moves)  # Player1 plays the medicine card
        moves = [Move(opponent=self.player1, opponent_organ=cards[0])]
        num_successful_moves = self.player2.play_card(self.state, cards[3], moves)  # Player2 plays the virus card
        organ = self.player1.get_organ_by_color(CardColor.RED)
        self.assertEqual(organ.state, OrganState.IMMUNISED)
        self.assertEqual(num_successful_moves, 0)

    def test_play_contagion_treatment(self):
        # Test playing the Contagion treatment card
        # Add infected organs to both players' bodies
        cards = [Organ(CardColor.RED), Organ(CardColor.BLUE), Organ(CardColor.RED), Organ(CardColor.BLUE)]
        self.player1.add_organ_to_body(cards[0])
        self.player1.add_organ_to_body(cards[1])
        self.player2.add_organ_to_body(cards[2])
        self.player2.add_organ_to_body(cards[3])
        player1_red_organ = self.player1.get_organ_by_color(CardColor.RED)
        player1_blue_organ = self.player1.get_organ_by_color(CardColor.BLUE)
        player2_red_organ = self.player2.get_organ_by_color(CardColor.RED)
        player2_blue_organ = self.player2.get_organ_by_color(CardColor.BLUE)
        player1_red_organ.add_virus(Virus(CardColor.RED))
        player1_blue_organ.add_virus(Virus(CardColor.BLUE))
        contagion_card = Contagion()
        self.player1.add_card_to_hand(contagion_card)
        moves = [Move(player_organ=cards[0], opponent=self.player2, opponent_organ=cards[2]), Move(player_organ=cards[1], opponent=self.player2, opponent_organ=cards[3])]
        self.player1.play_card(self.state, contagion_card, moves)  # Player1 plays the Contagion card
        # Check if the virus spread to player2's organ
        self.assertEqual(player2_red_organ.state, OrganState.INFECTED)
        self.assertEqual(player2_blue_organ.state, OrganState.INFECTED)

    def test_play_organ_thief_treatment(self):
        # Test playing the Organ Thief treatment card
        # Add a healthy organ to player1's body and an Organ Thief card to player2's hand
        red_organ = Organ(CardColor.RED)
        organ_thief = OrganThief()
        self.player1.add_organ_to_body(red_organ)
        self.player2.add_card_to_hand(organ_thief)
        moves = [Move(opponent=self.player1, opponent_organ=red_organ)]
        self.player2.play_card(self.state, organ_thief, moves)  # Player2 plays the Organ Thief card
        # Check if the organ was stolen from player1
        self.assertEqual(len(self.player1.body), 0)
        self.assertEqual(len(self.player2.body), 1)

    def test_play_organ_thief_not_allow_same_organs(self):
        # Test playing the Organ Thief treatment card to steal the card of the same color as in body
        # Add a healthy organ to players bodies and an Organ Thief card to player1's hand
        cards = [Organ(CardColor.RED), Organ(CardColor.RED), OrganThief()]
        self.player1.add_organ_to_body(cards[0])
        self.player2.add_organ_to_body(cards[1])
        self.player1.add_card_to_hand(cards[2])
        moves = [Move()]
        self.player1.play_card(self.state, cards[0], moves)
        moves = [Move()]
        self.player2.play_card(self.state, cards[1], moves)
        moves = [Move(opponent=self.player2, opponent_organ=cards[1])]
        with self.assertRaises(ValueError):
            self.player1.play_card(self.state, cards[2], moves)  # Player1 plays the Organ Thief card

    def test_play_transplant_treatment(self):
        # Test playing the Transplant treatment card
        # Add healthy organs of different colors to both players' bodies
        cards = [Organ(CardColor.RED), Organ(CardColor.BLUE), Transplant()]
        self.player1.add_organ_to_body(cards[0])
        self.player2.add_organ_to_body(cards[1])
        self.player2.add_card_to_hand(cards[2])
        moves = [Move(opponent=self.player1, player_organ=cards[1], opponent_organ=cards[0])]
        self.player2.play_card(self.state, cards[2], moves)  # Player2 plays the Transplant card
        # Check if the organs were swapped
        self.assertEqual(self.player1.body[0].color, CardColor.BLUE)
        self.assertEqual(self.player2.body[0].color, CardColor.RED)

    def test_play_latex_glove_treatment(self):
        # Test playing the Latex Glove treatment card
        # Add cards to player1's hand and a Latex Glove card to player2's hand
        cards = [Organ(CardColor.RED), Virus(CardColor.BLUE), LatexGlove()]
        self.player1.add_card_to_hand(cards[0])
        self.player1.add_card_to_hand(cards[1])
        self.player2.add_card_to_hand(cards[2])
        moves = [Move()]
        self.player2.play_card(self.state, cards[2], moves)  # Player2 plays the Latex Glove card
        # Check if player1's hand is empty
        self.assertEqual(len(self.player1.hand), 0)

    def test_play_medical_error_treatment(self):
        # Test playing the Medical Error treatment card
        # Add different organs to both players' bodies
        player1_organs = [
            Organ(CardColor.RED),
            Organ(CardColor.BLUE),
            Organ(CardColor.YELLOW)
        ]
        player2_organs = [
            Organ(CardColor.RED)
        ]

        for organ in player1_organs:
            self.player1.add_organ_to_body(organ)
        for organ in player2_organs:
            self.player2.add_organ_to_body(organ)

        medical_error = MedicalError()
        self.player2.add_card_to_hand(medical_error)
        moves = [Move(opponent=self.player1)]

        self.player2.play_card(self.state, medical_error, moves)

        # Check if the organs were swapped
        self.assertEqual(len(self.player1.body), 1)
        self.assertEqual(len(self.player2.body), 3)
        self.assertNotIn(medical_error, self.player2.hand)
        self.assertEqual(self.player1.body, player2_organs)
        self.assertEqual(self.player2.body, player1_organs)

    def test_player_draw_card(self):
        # Test player drawing a card from the deck
        initial_deck_size = len(self.state.deck.cards)
        self.player1.draw_card(self.state.deck)
        self.assertEqual(len(self.state.deck.cards), initial_deck_size - 1)
        self.assertEqual(len(self.player1.hand), 1)

    def test_player_discard_card(self):
        # Test player discarding a card
        card = Organ(CardColor.RED)
        self.player1.add_card_to_hand(card)
        self.player1.discard_card(self.state, 0)
        self.assertIn(card, self.state.deck.discard_pile)
        self.assertEqual(len(self.player1.hand), 0)

    def test_player_play_organ(self):
        # Test player playing an organ card
        red_organ = Organ(CardColor.RED)
        self.player1.add_card_to_hand(red_organ)
        moves = [Move()]
        self.player1.play_card(self.state, red_organ, moves)
        self.assertIn(red_organ, self.player1.body)
        self.assertEqual(len(self.player1.hand), 0)

    def test_player_cannot_play_if_no_cards(self):
        # Test that player cannot play a card that is not in their hand
        with self.assertRaises(IndexError):
            self.player1.get_hand_card_by_id(0)


if __name__ == '__main__':
    unittest.main()
