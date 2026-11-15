import asyncio
import json
import logging
import websockets
from websockets.server import serve

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
clientes_conectados = set()

async def gerenciador_conexao(websocket):
    clientes_conectados.add(websocket)
    logging.info(f"Nova conexão estabelecida. Total de clientes: {len(clientes_conectados)}")
    
    try:
        async for mensagem_bruta in websocket:
            logging.info(f"Mensagem recebida: {mensagem_bruta}")
            try:
                dados = json.loads(mensagem_bruta)
            except json.JSONDecodeError:
                dados = {"cliente": "Anônimo", "item": mensagem_bruta}
            payload = json.dumps({
                "tipo": "NOVO_PEDIDO",
                "cliente": dados.get("cliente", "Cliente"),
                "item": dados.get("item", "Café Expresso")
            })
            if clientes_conectados:
                await asyncio.gather(
                    *[cliente.send(payload) for cliente in clientes_conectados]
                )
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clientes_conectados.remove(websocket)
        logging.info(f"Conexão encerrada. Total de clientes restantes: {len(clientes_conectados)}")

async def main():
    async with serve(gerenciador_conexao, "localhost", 8765):
        logging.info("Servidor WebSocket iniciado em ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())