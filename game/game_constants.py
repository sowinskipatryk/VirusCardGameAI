from enums import CardColor


class GameConstants:
    MIN_PLAYERS: int = 2
    MAX_PLAYERS: int = 6
    HAND_SIZE: int = 3
    NUM_HEALTHY_ORGANS_TO_WIN: int = 4

    NUM_COLORED_ORGANS: int = 5
    NUM_COLORED_VIRUSES: int = 4
    NUM_COLORED_MEDICINES: int = 4

    NUM_WILD_ORGANS: int = 1
    NUM_WILD_VIRUSES: int = 1
    NUM_WILD_MEDICINES: int = 4

    NUM_CONTAGIONS: int = 2
    NUM_ORGAN_THIEVES: int = 3
    NUM_MEDICAL_ERRORS: int = 1
    NUM_TRANSPLANTS: int = 3
    NUM_LATEX_GLOVES: int = 1

    NUM_TOTAL_CARDS = ((NUM_COLORED_ORGANS + NUM_COLORED_VIRUSES + NUM_COLORED_MEDICINES) * len(list(CardColor))
                       + NUM_WILD_ORGANS
                       + NUM_WILD_VIRUSES
                       + NUM_WILD_MEDICINES
                       + NUM_CONTAGIONS
                       + NUM_ORGAN_THIEVES
                       + NUM_MEDICAL_ERRORS
                       + NUM_TRANSPLANTS
                       + NUM_LATEX_GLOVES
                       )
