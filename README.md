

# Virus Card Game AI

A modular, extensible framework for simulating and experimenting with AI and human players in the popular Virus! Card Game implementation. This project supports a variety of player strategies, including rule-based, random, NEAT, and human input.

---

## Features

- **Multiple AI Player Types:**  
  - Random, Rule-Based, Strategy-Based, NEAT (NeuroEvolution), 
  - MCTS (Monte Carlo Tree Search) **_COMING SOON_**
- **Human Player Support:**  
  - Play interactively via console input.
- **Player Factory:**  
  - Easily instantiate and manage different player types.
- **Game Constants and Rules:**  
  - Centralized configuration for game rules and card counts.
- **Extensible Design:**  
  - Add new player types or strategies with minimal changes.

---

## Project Structure

```
/players/
    __init__.py           # PlayerFactory and player type imports
    base_player.py        # Abstract base class for all players
    human_player.py       # Human player (console input)
    random_player.py      # Random-move player
    neat_player/
        __init__.py            # NEAT player logic and config loading
        training/
            neat-config.txt         # NEAT configuration file
            best_genome.pkl         # Trained genome checkpoint
    strategy_based_ai/
        __init__.py            # Strategy-based AI player logic
        strategies.py          # Specific strategies for AI
    rule_based_ai.py      # Rule-based AI player
/game/
    game_constants.py     # GameConstants (rules, card counts)
    game_manager.py       # GameManager (game loop, win condition)
    game_state.py         # GameState (current state, player turns)
/enums/              # Enums (Action, CardColor, CardType, OrganState, PlayerType, TreatmentName)
/models/             # Game specific object classes
/tests/              # Unit tests
/interface/          # Interface classes for game presentation
    __init__.py            # Presenter selection and initialization
    base_presenter.py      # Abstract base presenter class
    blank_presenter.py     # No-op presenter (for silent runs/testing)
    cli_presenter.py       # Command-line interface presenter
...
```

---

## Player System

Players are instantiated and managed using the `PlayerFactory` class. Each player type is mapped to a class, allowing for flexible game configuration.

### Supported Player Types

- `HUMAN`
- `RANDOM`
- `NEAT_AI`
- `RULE_BASED_AI`
- `STRATEGY_BASED_AI`

### Example: Creating Players

```python
from players import PlayerFactory
from enums import PlayerType

factory = PlayerFactory()
factory.add_player(PlayerType.HUMAN, "Alice")
factory.add_player(PlayerType.RULE_BASED_AI, "Bot1")
# ...add more players as needed

assert factory.is_valid()  # Ensure player count is within allowed range
```

---

## Running the Game

The game is managed by the `GameManager` class, which takes a configured `PlayerFactory` and runs the main game loop.

```python
from game.game_manager import GameManager

manager = GameManager(factory)
winner = manager.run()
print(f"Winner: {winner.name}")
```

---

## Extending the System

To add a new player type:

1. **Implement a new player class** (subclassing `BasePlayer`).
2. **Add it to the `PLAYER_TYPE_TO_PLAYER_CLASS` mapping** in `PlayerFactory`.
3. **Update the `PlayerType` enum** in `/enums/player_types.py`.

---

## Requirements

- Python 3.8+
- [NEAT-Python](https://neat-python.readthedocs.io/) (for NEAT)
- Other dependencies as required by your environment

---

## License

MIT License

---

## Acknowledgements

- Inspired by the [Virus! Card Game](https://tranjisgames.com/shop/trg-001vir-virus-1104)
- AI techniques: NEAT, MCTS (soon)

---

## Contact

For questions or contributions, please open an issue or submit a pull request.

