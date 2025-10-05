# server/events/builders.py
from typing import Dict, List
from pydantic import BaseModel


# -----------------------------
# Base event class
# -----------------------------
class Event(BaseModel):
    type: str


# -----------------------------
# Specific event classes
# -----------------------------
class InitEvent(Event):
    type: str = "init"
    client_id: str
    player_count: int
    players: Dict[str, Dict[str, object]]  # {client_id: {"position": [x, y], "direction": str}}


class PlayerJoinEvent(Event):
    type: str = "player_join"
    id: str
    position: List[int]
    direction: str


class PlayerLeaveEvent(Event):
    type: str = "player_leave"
    id: str


class PlayerUpdateEvent(Event):
    type: str = "player_update"
    id: str
    position: List[int]
    direction: str


# -----------------------------
# Builder helper functions
# -----------------------------
def init_event(client_id: str, connected_clients: dict) -> str:
    """Build JSON string for init event."""
    players = {
        cid: {"position": info["position"], "direction": info["direction"]}
        for cid, info in connected_clients.items() if cid != client_id
    }
    event = InitEvent(
        client_id=client_id,
        player_count=len(connected_clients),
        players=players,
    )
    return event.model_dump_json()


def player_join_event(client_id: str, info: dict) -> str:
    event = PlayerJoinEvent(
        id=client_id,
        position=info["position"],
        direction=info["direction"],
    )
    return event.model_dump_json()


def player_leave_event(client_id: str) -> str:
    event = PlayerLeaveEvent(id=client_id)
    return event.model_dump_json()


def player_update_event(client_id: str, info: dict) -> str:
    event = PlayerUpdateEvent(
        id=client_id,
        position=info["position"],
        direction=info["direction"],
    )
    return event.model_dump_json()
