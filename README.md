# ABCDE — Global Maritime Strategy Simulator

ABCDE (Army, Business, Colony, Diplomacy, Empire) is a turn-based strategy game about maritime trade, industrial growth, diplomacy, and naval conflict. Six asymmetric powers compete on a world map whose economic and military systems continue to affect one another over many rounds.

This project began as an original tabletop ruleset and was later developed into a playable Python/Pygame simulation. The current prototype supports both human-controlled countries and autonomous agents, making it useful for playtesting complex rule interactions and long-term balance.

## Demo

> Add a 20–40 second GIF here showing country selection, a trade route, ship movement, and a battle or news event.

## What makes the game interesting

- **Interdependent systems:** ports, factories, resources, trade routes, taxes, insurance, treaties, and warfare share the same evolving game state.
- **Asymmetric powers:** the United Kingdom, Russia, China, Japan, the United States, and Pirates have different strategic priorities.
- **Dynamic world events:** plagues, monsoons, market changes, and other news events temporarily alter movement, prices, and access.
- **Meaningful logistics:** ships travel through a weighted global route graph; trade requires route planning, port access, storage, upkeep, and risk management.
- **Human or AI control:** players choose which countries to control while the remaining countries use rule-based agents.
- **Replayable simulation:** randomized setup and interacting economic systems produce different strategic outcomes each game.

## Engineering highlights

- Models persistent game state with Python data classes for players, ships, ports, trade cards, treaties, news events, and historical events.
- Uses graph algorithms to calculate shortest maritime paths and movement distance between ports.
- Separates geographic, colony, and trade-route data from the main game loop.
- Resolves multi-step state transitions for construction, trade, storage, taxation, ship upkeep, insurance, port policy, and combat.
- Records transactions and round-by-round events for debugging, balance analysis, and end-of-game history export.
- Implements a Pygame interface with a projected world map, interactive ports and routes, contextual actions, and country dashboards.

## Quick start

### Requirements

- Python 3.10+
- Pygame

```bash
git clone https://github.com/patrick528300/ABCDE-game-terminal.git
cd ABCDE-game-terminal
python3 -m pip install pygame
python3 abcde_pygame_map.py
```

For the version with autonomous country agents:

```bash
python3 abcde_pygame_ai.py
```

At startup, select at least one human-controlled country. Unselected countries are controlled by the game agents.

## Core game loop

1. Manage money, resources, ports, factories, ships, and diplomatic access.
2. Invest in trade opportunities and move merchant ships through the route network.
3. Build infrastructure or military power while paying maintenance and port costs.
4. Respond to market changes, news events, piracy, and other countries' decisions.
5. Finish the selected number of rounds with the strongest combined economic and strategic position.

## Project structure

| File | Purpose |
| --- | --- |
| `abcde_pygame_map.py` | Main playable Pygame implementation |
| `abcde_pygame_ai.py` | Extended simulation with autonomous country agents |
| `Colony_dataBase.py` | Port and colony definitions |
| `trade_route_dataBase.py` | Trade-route data and helper functions |
| `port_geo_coords_edited.py` | Geographic coordinates used by the world map |
| `News_function.py` | Earlier news and resource-event logic |
| `project.py` | Earlier terminal prototype and rules implementation |
| `THE RULES OF ABCDE (1).docx` | Original tabletop rules reference |

## Design and development

I designed the original rules, factions, economy, trade network, and risk/reward structure, then directed their translation into a playable software system. My work focused on specifying state transitions, integrating interacting subsystems, debugging edge cases, and repeatedly playtesting and rebalancing the simulation.

This repository is a prototype rather than a finished commercial game. The most important next step is to separate the large Pygame modules into smaller engine, UI, data, and agent packages and add automated tests for economic and combat invariants.

## Roadmap

- Refactor the game engine away from rendering and input code
- Add deterministic seeds and save/load support
- Add unit tests for trade, combat, movement, and economy rules
- Improve agent evaluation and balance reporting
