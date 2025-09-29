from enum import StrEnum


class PlayerType(StrEnum):
    HUMAN = "Human"
    RANDOM = "Random"
    NEAT_AI = "NEAT_AI"
    RULE_BASED_AI = "RuleBasedAI"
    STRATEGY_BASED_AI = "StrategyBasedAI"
    DQN_AI = 'DQN_AI'
    MCTS_AI = 'MCTS_AI'
    ISMCTS_AI = 'ISMCTS_AI'
