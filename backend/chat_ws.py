from fastapi import WebSocket, WebSocketDisconnect
from typing import List

# Simple in-memory list of connections
active_connections: List[WebSocket] = []

# Accept and add the websocket connection to the active list
async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

# Remove websocket from active list
def disconnect(websocket: WebSocket):
    if websocket in active_connections:
        active_connections.remove(websocket)

# Send message to a specific websocket
async def send_personal_message(message: str, websocket: WebSocket):
    await websocket.send_text(message)

# Broadcast message to all clients except sender
async def broadcast(message: str, sender: WebSocket):
    for connection in active_connections:
        if connection != sender:
            await connection.send_text(message)

# WebSocket endpoint handler (called from main.py)
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(f"[user] {data}", sender=websocket)
    except WebSocketDisconnect:
        disconnect(websocket)
