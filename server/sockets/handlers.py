# server/sockets/handlers.py
import uuid
import json
import logging
from litestar import WebSocket

from server.state import server_state
from server.events.builders import (
    init_event,
    player_join_event,
    player_leave_event,
    player_update_event,
)
from server.events.broadcaster import broadcast
from server.game.logic import GameLogic

logger = logging.getLogger("server")


async def handle_accept(socket: WebSocket) -> str:
    """Register a new client and notify others."""
    client_id = str(uuid.uuid4())
    server_state.register_client(client_id, socket)

    await socket.send_text(init_event(client_id, server_state.all_clients()))
    await broadcast(
        player_join_event(client_id, server_state.get_client(client_id)),
        exclude=client_id,
    )
    logger.info("Client connected: %s", client_id)
    return client_id


async def handle_disconnect(socket: WebSocket) -> None:
    """Remove client on disconnect and notify others."""
    client_id = server_state.get_client_by_socket(socket)
    if client_id:
        server_state.remove_client(client_id)
        await broadcast(player_leave_event(client_id))
        logger.info("Client disconnected: %s", client_id)


async def handle_receive(socket: WebSocket, data: str) -> None:
    """Process incoming messages from a client."""
    client_id = server_state.get_client_by_socket(socket)
    if not client_id:
        return

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON from %s: %s", client_id, data)
        return

    move = parsed.get("move")
    if not isinstance(move, str) or move not in {"up", "down", "left", "right", "up_left", "up_right", "down_left", "down_right"}:
        logger.warning("Invalid move from %s: %s", client_id, move)
        return

    if GameLogic.move_player(client_id, move):
        current = server_state.get_client(client_id)
        await broadcast(player_update_event(client_id, current))
