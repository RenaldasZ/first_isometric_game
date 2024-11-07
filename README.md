# first_isometric_game

## Isometric Ground Effect with Player

#### This model provides a basic isometric ground effect with a player tile that can move in a 2D grid. The game visually simulates 3D-like movement using isometric projections and allows for simple grid-based navigation.

```
- python -m venv venv
- venv\scripts\activate

- pip install pygame-ce
- pip install litestar[standard]
- pip install websocket-client

or:

- pip install requirements.txt


run server:
uvicorn server:app --reload

run client:
python main.py
```

Updates:

- Class based WebSocket handling
- Litestar implementation

Screenshots:

![alt text](images/v1.png)