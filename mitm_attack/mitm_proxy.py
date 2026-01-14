import asyncio
import websockets
import json
import os
from colorama import Fore, Style, init

init(autoreset=True)

REAL_SERVER_URI = os.getenv("REAL_SERVER_URI", "ws://localhost:8765")
MITM_PORT = 8766

print(f"{Fore.CYAN}[Config] REAL_SERVER_URI: {REAL_SERVER_URI}")


async def mitm_handler(client_ws):
    print(f"{Fore.RED}[MitM] Vítima conectada ao Proxy.")

    try:
        async with websockets.connect(REAL_SERVER_URI) as server_ws:

            async def forward_client_to_server():
                async for message in client_ws:
                    print(f"\n{Fore.YELLOW}[MitM Intercept] Cliente -> Servidor:")
                    analyze_message(message)
                    await server_ws.send(message)

            async def forward_server_to_client():
                async for message in server_ws:
                    print(f"\n{Fore.MAGENTA}[MitM Intercept] Servidor -> Cliente:")
                    analyze_message(message)
                    await client_ws.send(message)

            await asyncio.gather(forward_client_to_server(), forward_server_to_client())
    except Exception as e:
        print(f"{Fore.RED}[MitM] Conexão encerrada: {e}")


def analyze_message(raw_message):
    try:
        data = json.loads(raw_message)
        msg_type = data.get("type")
        sender = data.get("sender_id")
        content = data.get("content")

        print(f"  Tipo: {msg_type}")
        print(f"  Remetente: {sender}")

        if msg_type == "text":
            print(f"  {Fore.RED}Conteúdo (Cifrado): {content[:50]}...")
        elif msg_type == "handshake":
            print(f"  {Fore.BLUE}Conteúdo (Chave Pública): {content[:50]}...")

    except Exception:
        print(f"  Mensagem Raw (Não-JSON): {raw_message}")


async def start_mitm():
    print(f"{Fore.RED}--- Man-in-the-Middle Proxy Iniciado na porta {MITM_PORT} ---")
    print(
        f"{Fore.RED}Conecte os clientes em ws://localhost:{MITM_PORT} para interceptar."
    )

    async with websockets.serve(mitm_handler, "0.0.0.0", MITM_PORT):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(start_mitm())
    except KeyboardInterrupt:
        print("MitM Parado.")
