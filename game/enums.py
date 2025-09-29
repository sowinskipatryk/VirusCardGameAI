from enum import StrEnum, IntEnum


class Action(StrEnum):
    PLAY = 'Play'
    DISCARD = 'Discard'


class CardColor(StrEnum):
    RED = 'Red'
    YELLOW = 'Yellow'
    BLUE = 'Blue'
    GREEN = 'Green'
    WILD = 'Wild'


class CardType(StrEnum):
    TREATMENT = "Treatment"
    ORGAN = "Organ"
    MEDICINE = "Medicine"
    VIRUS = "Virus"


class OrganState(IntEnum):
    INFECTED = 1
    HEALTHY = 2
    VACCINATED = 3
    IMMUNISED = 4


class PlayerType(StrEnum):
    HUMAN = "Human"
    RANDOM = "Random"
    NEAT_AI = "NEAT_AI"
    RULE_BASED_AI = "RuleBasedAI"
    STRATEGY_BASED_AI = "StrategyBasedAI"
    DQN_AI = 'DQN_AI'
    MCTS_AI = 'MCTS_AI'
    ISMCTS_AI = 'ISMCTS_AI'


class TreatmentName(StrEnum):
    TRANSPLANT = "Transplant"
    ORGAN_THIEF = "OrganThief"
    CONTAGION = "Contagion"
    LATEX_GLOVE = "LatexGlove"
    MEDICAL_ERROR = "MedicalError"
