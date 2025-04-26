import neat
import os
import pickle
from players import PlayerFactory
from game.game_manager import GameManager
from interface.graph_reporter import LiveGraphReporter
from enums import PlayerType


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        player_factory = PlayerFactory()

        ai_player = player_factory.add_player(PlayerType.NEAT_AI, "AI", genome=genome, config=config)

        for i in range(3):
            player_factory.add_player(PlayerType.RULE_BASED_AI, f"Bot{i + 1}")

        game = GameManager(player_factory)
        winner = game.run()
        genome.fitness = ai_player.get_final_score()
        if ai_player is winner:
            genome.fitness += 50


def eval_genomes_tournament(genomes, config):
    # Initialize fitness to zero for all genomes
    for _, genome in genomes:
        genome.fitness = 0

    # Create all possible groups of 4 genomes
    if len(genomes) < 4:
        return  # Not enough genomes to form a match

    # Shuffle genomes to ensure random matchups
    import random
    random.shuffle(genomes)

    group_size = 4
    num_groups = len(genomes) // group_size

    for i in range(num_groups):
        group = genomes[i * group_size : (i + 1) * group_size]
        player_factory = PlayerFactory()
        ai_players = []

        # Create 4 AI players with their genomes
        for j, (genome_id, genome) in enumerate(group):
            player = player_factory.add_player(PlayerType.NEAT_AI, f"AI{j + 1}", genome=genome, config=config)
            ai_players.append((genome, player))

        # Run the game
        game = GameManager(player_factory)
        winner = game.run()

        # Assign fitness based on final score and winning bonus
        for genome, player in ai_players:
            genome.fitness += player.get_final_score()
            if player is winner:
                genome.fitness += 300


def run_training(cfg_path, genome_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         cfg_path)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    population.add_reporter(LiveGraphReporter())
    population.add_reporter(neat.Checkpointer(generation_interval=50, filename_prefix='neat-checkpoint-'))

    # population = neat.Checkpointer.restore_checkpoint('neat-checkpoint-29')

    winner = population.run(eval_genomes, 1000)
    with open(genome_path, "wb") as f:
        pickle.dump(winner, f)


if __name__ == "__main__":
    CURRENT_DIR = os.path.dirname(__file__)
    config_path = os.path.join(CURRENT_DIR, "neat-config.txt")
    best_genome_path = os.path.join(CURRENT_DIR, "best_genome.pkl")
    run_training(config_path, best_genome_path)
