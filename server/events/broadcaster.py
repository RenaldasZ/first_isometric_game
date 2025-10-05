# server/events/broadcaster.py
import logging
from server.state import server_state

logger = logging.getLogger("server")


async def broadcast(message: str, exclude: str | None = None) -> None:
    """Send a message to all connected clients, optionally excluding one."""
    to_remove = []
    for cid, client in server_state.all_clients().items():
        if cid == exclude:
            continue
        try:
            await client["socket"].send_text(message)
        except Exception as e:
            logger.error("Error sending message to %s: %s", cid, e)
            to_remove.append(cid)

    # Clean up failed clients
    for cid in to_remove:
        server_state.remove_client(cid)
        logger.info("Removed client %s due to send failure", cid)
