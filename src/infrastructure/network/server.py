import asyncio
import websockets
import logging
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatServer")


class ChatServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.connected_clients = set()

    async def register(self, websocket: WebSocketServerProtocol):
        self.connected_clients.add(websocket)
        logger.info(f"Novo cliente conectado. Total: {len(self.connected_clients)}")

    async def unregister(self, websocket: WebSocketServerProtocol):
        self.connected_clients.remove(websocket)
        logger.info(f"Cliente desconectado. Total: {len(self.connected_clients)}")

    async def broadcast(self, message: str, sender: WebSocketServerProtocol):
        if not self.connected_clients:
            return

        for client in self.connected_clients:
            if client != sender:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    pass

    async def handler(self, websocket: WebSocketServerProtocol):
        await self.register(websocket)
        try:
            async for message in websocket:
                logger.info(f"Mensagem recebida (Relay): {message[:50]}...")
                await self.broadcast(message, websocket)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def start(self):
        async with websockets.serve(self.handler, self.host, self.port):
            logger.info(f"Servidor rodando em ws://{self.host}:{self.port}")
            await asyncio.Future()


if __name__ == "__main__":
    server = ChatServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Servidor parado.")
