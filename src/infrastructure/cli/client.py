import asyncio
import websockets
import json
import sys
import aioconsole
from colorama import Fore, Style, init

from src.domain.entities import Message, MessageType
from src.application.services.crypto_service import CryptoService

init(autoreset=True)


class ChatClient:
    def __init__(self, uri: str, username: str):
        self.uri = uri
        self.username = username
        self.crypto_service = CryptoService()
        self.private_key, self.public_key = self.crypto_service.generate_key_pair()
        self.shared_key = None
        self.websocket = None

    async def send_handshake(self):
        print(f"{Fore.YELLOW}[System] Enviando Handshake (Minha Chave Pública)...")
        msg = Message(
            type=MessageType.HANDSHAKE,
            sender_id=self.username,
            content=self.public_key.decode("utf-8"),
        )
        await self.websocket.send(msg.model_dump_json())

    async def handle_handshake(self, message: Message):
        if message.sender_id == self.username:
            return

        print(f"{Fore.YELLOW}[System] Handshake recebido de {message.sender_id}.")
        peer_public_key = message.content.encode("utf-8")

        try:
            new_shared_key = self.crypto_service.derive_shared_key(
                self.private_key, peer_public_key
            )

            if self.shared_key is None:
                self.shared_key = new_shared_key
                print(
                    f"{Fore.GREEN}[System] Chave Compartilhada Derivada com Sucesso! 🔒"
                )
                print(
                    f"{Fore.CYAN}[Debug] Shared Key (Hex): {self.shared_key.hex()[:10]}..."
                )

                print(
                    f"{Fore.YELLOW}[System] Respondendo com meu Handshake para garantir conexão mútua..."
                )
                await self.send_handshake()
            else:
                print(
                    f"{Fore.CYAN}[System] Handshake recebido, mas conexão já segura. Ignorando para evitar loop."
                )

        except Exception as e:
            print(f"{Fore.RED}[Error] Falha no Handshake: {e}")

    async def send_message(self, text: str):
        if not self.shared_key:
            print(
                f"{Fore.RED}[Error] Nenhuma conexão segura estabelecida. Aguarde o handshake."
            )
            return

        ciphertext, iv, tag = self.crypto_service.encrypt_message(text, self.shared_key)

        msg = Message(
            type=MessageType.TEXT,
            sender_id=self.username,
            content=ciphertext,
            iv=iv,
            tag=tag,
        )
        await self.websocket.send(msg.model_dump_json())

    async def receive_loop(self):
        try:
            async for raw_message in self.websocket:
                try:
                    data = json.loads(raw_message)
                    message = Message(**data)

                    if message.type == MessageType.HANDSHAKE:
                        await self.handle_handshake(message)

                    elif message.type == MessageType.TEXT:
                        if message.sender_id == self.username:
                            continue

                        if not self.shared_key:
                            print(
                                f"{Fore.RED}[!] Mensagem criptografada recebida, mas sem chave para decifrar."
                            )
                            continue

                        try:
                            plaintext = self.crypto_service.decrypt_message(
                                message.content,
                                message.iv,
                                message.tag,
                                self.shared_key,
                            )
                            print(f"\n{Fore.GREEN}[{message.sender_id}]: {plaintext}")
                        except Exception as e:
                            print(
                                f"\n{Fore.RED}[!] Falha ao descriptografar mensagem de {message.sender_id}: {e}"
                            )

                except Exception as e:
                    print(f"{Fore.RED}[Error] Erro ao processar mensagem: {e}")
        except websockets.exceptions.ConnectionClosed:
            print(f"{Fore.RED}[System] Conexão fechada pelo servidor.")

    async def input_loop(self):
        print(f"{Fore.BLUE}--- Chat Seguro Iniciado ---")
        print(f"{Fore.BLUE}Digite sua mensagem e pressione Enter.")

        while True:
            text = await aioconsole.ainput("")
            if text.lower() == "/quit":
                break
            if text.lower() == "/handshake":
                await self.send_handshake()
                continue

            await self.send_message(text)

    async def start(self):
        async with websockets.connect(self.uri) as websocket:
            self.websocket = websocket
            print(f"{Fore.GREEN}[System] Conectado ao servidor {self.uri}")

            await self.send_handshake()

            await asyncio.gather(self.receive_loop(), self.input_loop())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python client.py <username> [uri]")
        sys.exit(1)

    username = sys.argv[1]
    uri = sys.argv[2] if len(sys.argv) > 2 else "ws://localhost:8765"

    client = ChatClient(uri, username)
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        print("Saindo...")
