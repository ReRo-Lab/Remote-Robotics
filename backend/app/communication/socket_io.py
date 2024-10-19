# Author: Ujwal N K
# Created on: 2024, Oct 18
# Socket communication to-from the front-end for user-code exception & print

import socketio

# SocketIO Server Instance
# Allow CORS for all origins for communication between the user & back-end directly
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

socket_app = socketio.ASGIApp(sio)

# SocketIO Event Handlers
@sio.event
async def connect(sid, environ):
    print("Client connected", sid)
    await sio.emit("message", "Connected")

async def user_dump_printer(data, bot):
    """Send bot dump (user-printed) data to user"""
    await sio.emit("print", {"print" : data, "bot" : bot})

async def user_exception_printer(data, bot):
    """Send bot exception to user"""
    await sio.emit("exception", {"print" : data, "bot" : bot})

