# client/core/network.py
import websocket
import json
import time
import logging
import threading
from typing import Optional
from client.core.state import GameState

logger = logging.getLogger("client.network")
logger.setLevel(logging.DEBUG)

class Network:
    """WebSocket client that pushes parsed messages into GameState.message_queue."""

    def __init__(self, url: str, state: GameState):
        self.url = url
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_connected = False
        self.state = state
        self._stop_flag = threading.Event()

    def _on_open(self, ws):
        logger.info("WebSocket connected")
        self.is_connected = True
        self.state.connection_status = "Connected"

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket disconnected")
        self.is_connected = False
        self.state.connection_status = "Disconnected"

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.state.push_message(data)
        except Exception as e:
            logger.error("Failed to parse message: %s", e)

    def _on_error(self, ws, error):
        logger.error("WebSocket error: %s", error)

    def connect(self):
        """Create a WebSocketApp instance and run it (blocking)."""
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_close=self._on_close,
            on_message=self._on_message,
            on_error=self._on_error,
        )
        self.ws.run_forever()

    def run_forever(self):
        """Keep trying to connect. Intended to be run in a daemon thread."""
        while not self._stop_flag.is_set():
            try:
                logger.debug("Attempting websocket connection to %s", self.url)
                self.connect()
            except Exception as e:
                logger.error("WebSocket run_forever error: %s", e)
            # short delay before reconnecting
            time.sleep(2)

    def start(self) -> threading.Thread:
        thread = threading.Thread(target=self.run_forever, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        self._stop_flag.set()
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass

    def send_move(self, direction: str) -> None:
        if self.ws and self.is_connected:
            try:
                self.ws.send(json.dumps({"move": direction}))
            except Exception as e:
                logger.error("Failed to send move: %s", e)
        else:
            logger.debug("Cannot send move, not connected")
