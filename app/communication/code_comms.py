# Author: Ujwal N K
# Date: 2024, Sep 20
# Communication from the user to the bot handled by the server

import asyncio
from typing import Annotated

import requests
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile

from datetime import datetime, timedelta, timezone

from ..database import operations as ds
from ..core.schema import Token, TokenData, User, UserInDB

from ..core.core import get_current_active_user, iot_bot_access, ros_bot_access

from ..communication import bot_comms as bc
from ..communication import code_comms as cc
from ..communication.check_imports import check_imports
import httpx

router = APIRouter(prefix="/bot")


@router.post(
    "/iot/code",
    responses={
        200: {"description": "Code pushed successfully"},
        400: {"description": "Invalid imports, ensure code has no import statements"},
        500: {"description": "Internal Server Error"},
    },
)
async def push_code(
    current_user: Annotated[User, Depends(iot_bot_access)], file: UploadFile
) -> bool:
    """
    Function to save the code to a temp folder. Code that is sent by the user.
    The sent code needs to be dumped into the IoT Bot
    """
    try:
        # Intentionally changing the file extension to ensure no accidental runs
        file_path: str = f"/tmp/iot/iot_bot.code"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        imports: list = check_imports("/tmp/iot/iot_bot.code")

        print(imports)

        if len(imports) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid imports: {imports}",
            )

        else:
            bc.push_code(bc.IP_IOT_BOT, "/tmp/iot/iot_bot.code")

            return True

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return False


@router.get(
    "/iot/stop",
    responses={
        # TODO: Send code for no-code running on the bot
        200: {"description": "IoT Bot stopped successfully"},
        500: {"description": "Internal Server Error"},
    },
)
async def stop_iot_bot(
    current_user: Annotated[User, Depends(iot_bot_access)],
) -> None | bool:
    """Emergency stop for the IoT BOT"""
    # TODO: Implement stop message over socket stream
    # return True

    result = await asyncio.to_thread(requests.get, "http://" + bc.IP_IOT_BOT + "/stop_code")


@router.post(
    "/ros/code",
    responses={
        200: {"description": "Code pushed successfully"},
        400: {"description": "Invalid imports, ensure code has no import statements"},
        500: {"description": "Internal Server Error"},
    },
)
async def push_code(
    current_user: Annotated[User, Depends(ros_bot_access)], file: UploadFile
) -> bool:
    """
    Function to save the code to a temp folder. Code that is sent by the user.
    The sent code needs to be dumped into the ROS Bot
    """
    try:
        # Intentionally changing the file extension to ensure no accidental runs
        file_path: str = f"/tmp/ros/ros_bot.code"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        imports: list = check_imports("/tmp/ros/ros_bot.code")

        print(imports)

        if len(imports) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid imports: {imports}",
            )

        else:
            bc.push_code(bc.IP_ROS_BOT, "/tmp/ros/ros_bot.code")

            return True

    except HTTPException as e:
        raise e

    except Exception as e:

        print(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    # return False


@router.get(
    "/ros/stop",
    responses={
        # TODO: Send code for no-code running on the bot
        200: {"description": "IoT Bot stopped successfully"},
        500: {"description": "Internal Server Error"},
    },
)
async def stop_ros_bot(
    current_user: Annotated[User, Depends(ros_bot_access)],
) -> bool:
    """Emergency stop for the ROS Bot"""
    # TODO: Implement stop message over socket stream
    return True
