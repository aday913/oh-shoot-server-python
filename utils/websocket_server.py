import asyncio
import websockets

connected_clients = set()

async def handle_client(websocket):
    # Register client
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # Broadcast the received message
            await asyncio.gather(*(client.send(message) for client in connected_clients if not client.close))
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Unregister client
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
