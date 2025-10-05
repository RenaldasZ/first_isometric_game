# server/app.py
import logging
from litestar import Litestar, WebSocket
from litestar.handlers import WebsocketListener

from server.sockets.handlers import (
    handle_accept, handle_disconnect, handle_receive
)

logger = logging.getLogger("server")


class GameWebSocket(WebsocketListener):
    path = "/"

    async def on_accept(self, socket: WebSocket) -> None:
        await handle_accept(socket)

    async def on_disconnect(self, socket: WebSocket) -> None:
        await handle_disconnect(socket)

    async def on_receive(self, socket: WebSocket, data: str) -> None:
        await handle_receive(socket, data)


def create_app() -> Litestar:
    return Litestar([GameWebSocket])
