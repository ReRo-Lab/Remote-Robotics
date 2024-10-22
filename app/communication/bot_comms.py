# Author: Ujwal N K
# Date: 2024-01-25
# Communication from the server to the bots

from typing import Annotated
from fastapi import APIRouter, HTTPException, status

from ..communication import socket_io

import requests
from requests import Response

# Bot IP Address constants
IP_ROS_BOT = "localhost:8081"
IP_IOT_BOT = "localhost:8082"

# BOT Name strings
ROS_BOT = "ros"
IOT_BOT = "iot"

router = APIRouter()

def push_code(bot: str, file_path: str) -> bool:
    """
    Function to alert bot & send the code file from the server

    Makes a multipart POST request to the bot

    @param:
        bot (str): IP Address of the BOT
        file_path (str): File path
    """

    print("Alerting the bot")

    url: str = f"http://{bot}/push_code"

    try:
        # Open the file as binary
        with open(file_path, 'rb') as file:
            files = {'file': file}

            # Make a POST request
            response: Response = requests.post(url, files=files)
            response.raise_for_status()
            return True
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False
    

@router.get("/iot/dump")
async def dump_iot_data(data: str):
    """
    Print string from iot bot to the client

    data: str
    """
    print("Running...", data)
    await socket_io.user_dump_printer(data, IOT_BOT)
    return 200

@router.get("/iot/exception")
async def dump_iot_data(data: str):
    """
    Print string from iot bot to the client

    data: str
    """
    
    socket_io.user_exception_printer(data, IOT_BOT)


@router.get("/ros/dump")
async def dump_ros_data(data: str):
    """
    Print string from ros bot to the client

    data: str
    """
    
    socket_io.user_dump_printer(data, ROS_BOT)

@router.get("/ros/exception")
async def dump_ros_data(data: str):
    """
    Print string from ros bot to the client

    data: str
    """
    
    socket_io.user_exception_printer(data, ROS_BOT)
