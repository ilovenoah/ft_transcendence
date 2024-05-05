# websocket_server.py
import asyncio
import websockets
import json

connected = set()

async def handler(websocket, path):
    global connected
    connected.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            for conn in connected:
                if conn != websocket:
                    await conn.send(json.dumps(data))
    finally:
        connected.remove(websocket)

start_server = websockets.serve(handler, "0.0.0.0", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
