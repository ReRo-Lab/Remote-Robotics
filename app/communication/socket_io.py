# Author: Ujwal N K
# Created on: 2024, Oct 18
# Socket communication to-from the front-end for user-code exception & print

from ..database.operations import get_jwt
from ..core.core import admin_group
from ..core.core import SECRET_KEY, ALGORITHM

import socketio
import jwt


# SocketIO Server Instance
# Allow CORS for all origins for communication between the user & back-end directly
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

socket_app = socketio.ASGIApp(sio)

# SocketIO Event Handlers
@sio.event
async def connect(sid, environ):
    """
    Client onConnect for websocket

    JWT token will be authenticated for login purposes
    """

    # Check for JWT Authentication
    token = environ.get('HTTP_AUTHORIZATION')

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")


        # Check username registered
        if username is None:
            await sio.emit("Error: Username field NULL", sid=sid)
            print("Username is none")
            raise Exception

        # Check JWT Token
        elif (username not in admin_group) and (get_jwt(username)[0] != token):
            await sio.emit("Error: Invalid JWT token", sid=sid)
            raise Exception

    except Exception as e:
        print(e)
        await sio.emit("message", {"error": str(e)})
        await sio.disconnect(sid)
        return
    
    # Successful connect
    print("Client connected", sid)
    await sio.emit("message", "Connected")

async def user_dump_printer(data, bot):
    """Send bot dump (user-printed) data to user"""
    print("Sending data")
    await sio.emit("print", {"print" : data, "bot" : bot, "type": "info"})

async def user_exception_printer(data, bot):
    """Send bot exception to user"""
    await sio.emit("print", {"print" : data, "bot" : bot, "type": "error"})

