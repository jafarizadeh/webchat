from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os

app = FastAPI()

# Serve static files (frontend HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Connection class to track users
class Connection:
    def __init__(self, username: str, websocket: WebSocket):
        self.username = username
        self.websocket = websocket

# Active connections
active_connections: List[Connection] = []

# Accept and register connection
async def connect(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections.append(Connection(username, websocket))

# Remove connection on disconnect
def disconnect(websocket: WebSocket):
    for conn in active_connections:
        if conn.websocket == websocket:
            active_connections.remove(conn)
            break

# Broadcast message to all except sender
async def broadcast(message: str, sender_ws: WebSocket):
    for conn in active_connections:
        if conn.websocket != sender_ws:
            await conn.websocket.send_text(message)

# WebSocket endpoint with username in query param
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    username = websocket.query_params.get("username", "Anonymous")
    await connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(f"{username}: {data}", sender_ws=websocket)
    except WebSocketDisconnect:
        disconnect(websocket)

# Basic HTML frontend
@app.get("/")
async def get():
    html_path = os.path.join("static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
