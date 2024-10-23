from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core import core
from .communication import bot_comms ,code_comms, socket_io
from .database import operations
from .timeslot import timeslot_manager

app = FastAPI()

app.include_router(core.router)
app.include_router(timeslot_manager.router)
app.include_router(code_comms.router)
app.include_router(bot_comms.router)

app.mount("", socket_io.socket_app)

