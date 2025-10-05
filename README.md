# first_isometric_game

## Isometric Ground Effect with Player

#### This model provides a basic isometric ground effect with a player tile that can move in a 2D grid. The game visually simulates 3D-like movement using isometric projections and allows for simple grid-based navigation.

### Run from project root
```
1. Install libraries
        pip install requirements.txt

2. Run server.
        uvicorn server.main:app --reload

3. Client entrypoint.
        python -m client.main
```



### Folder structure:
```
first_isometric_game/
│
├── client/
│   ├── __init__.py
│   ├── main.py               # entrypoint to run pygame client
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── animation.py      # Animation system
│   │   ├── directions.py     # Centralized direction handlings
│   │   ├── grid.py           # Tile + isometric grid
│   │   ├── input.py          # Player movement inputs
│   │   ├── network.py        # WebSocket client
│   │   ├── player.py         # Player entity - position, animation, direction
│   │   └── state.py          # Game state container (local + remote players)
│   │
│   ├── scenes/
│   │   ├── __init__.py
│   │   └── game_scene.py     # Game loop: update(), draw(), handle_events()
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── hud.py            # HUD elements (status text, player count)
│   │
│   └── config.py             # client constants (screen size, colors, etc.)
│
├── assets/
│   └── media/                # sprites, images
│
│──server/
│   ├── __init__.py         
│   ├── app.py                # Litestar app factory (creates routes, listeners)
│   ├── config.py             # constants (GRID_WIDTH, GRID_HEIGHT, etc.)
│   ├── main.py               # entrypoint to run the server
│   ├── state.py              # global state container (registry, world size)
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   ├── broadcaster.py    # broadcast(message)
│   │   └── builders.py       # init_event, player_join_event, etc.
│   │
│   ├── game/
│   │   ├── __init__.py
│   │   └── logic.py          # Game logic, movement etc..
│   │
│   ├── sockets/
│   │   ├── __init__.py
│   │   └── handlers.py       # on_accept, on_disconnect, on_receive
│   └──
└──