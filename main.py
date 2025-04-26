from players import PlayerFactory
from game.game_manager import GameManager
from enums import PlayerType

from collections import defaultdict


def main():
    player_factory = PlayerFactory()

    player_factory.add_player(PlayerType.RULE_BASED_AI, "John")
    # player_factory.add_player(PlayerType.HUMAN, "John")
    # player_factory.add_player(PlayerType.NEAT_AI, "John")
    # player_factory.add_player(PlayerType.RANDOM, "John")

    player_factory.add_player(PlayerType.RANDOM, "George")
    player_factory.add_player(PlayerType.RANDOM, "Amy")
    player_factory.add_player(PlayerType.RANDOM, "Phil")

    game = GameManager(player_factory)
    winner = game.run()
    return winner


NUM_ITERATIONS = 100
winners = defaultdict(int)

for i in range(NUM_ITERATIONS):
    print(f'ITERATION {i+1}')
    curr_winner = main()
    winners[str(curr_winner)] += 1

print(f'FINAL STATS AFTER {NUM_ITERATIONS} ITERATIONS')
for winner, wins in winners.items():
    print(f'{winner}: {wins}')
