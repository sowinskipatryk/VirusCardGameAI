from players import PlayerFactory
from game.game_manager import GameManager
from enums import PlayerType


def main():
    player_factory = PlayerFactory()

    player_factory.add_player(PlayerType.RULE_BASED, "John")
    player_factory.add_player(PlayerType.RANDOM, "George")
    player_factory.add_player(PlayerType.RANDOM, "Amy")
    player_factory.add_player(PlayerType.RANDOM, "Phil")

    game = GameManager(player_factory)
    winner = game.run()
    return winner


main()
