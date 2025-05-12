from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os

app = FastAPI()

# Serve static files (frontend HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory list of WebSocket connections
active_connections: List[WebSocket] = []

# Accept and add a new WebSocket connection
async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

# Remove WebSocket connection when disconnected
def disconnect(websocket: WebSocket):
    if websocket in active_connections:
        active_connections.remove(websocket)

# Send a direct message to one WebSocket
async def send_personal_message(message: str, websocket: WebSocket):
    await websocket.send_text(message)

# Broadcast message to all WebSocket clients (except sender)
async def broadcast(message: str, sender: WebSocket):
    for connection in active_connections:
        if connection != sender:
            await connection.send_text(message)

# WebSocket endpoint route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(f"[user] {data}", sender=websocket)
    except WebSocketDisconnect:
        disconnect(websocket)

# Basic HTML frontend endpoint for testing
@app.get("/")
async def get():
    html_path = os.path.join("static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)