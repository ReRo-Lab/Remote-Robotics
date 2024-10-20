# Author: Ujwal N K
# Created On:
# Timeslot manager for fastapi

from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status

from datetime import datetime, timedelta, timezone

from ..database import operations as ds
from ..core.schema import Token, TokenData, User, UserInDB

from ..core.core import get_current_active_user, only_root_user, admin_plus

router = APIRouter()


@router.get(
    "/timeslot",
    responses={
        200: {"description": "Get all the timeslots"},
        401: {"description": "Not Authorized"},
    },
)
async def get_timeslots(
    current_user: Annotated[User, Depends(admin_plus)]
) -> list[User] | None:

    users: list[User] = ds.get_users()
    # Removing the root entry
    users.pop(0)
    return users


@router.get(
    "/timeslot/allot",
    responses={
        200: {"description": "Allot OK"},
        401: {
            "description": "User Not Authorized to allot timeslot. Only root user permitted"
        },
        404: {"description": "User not found"},
    },
)
async def set_timeslot(
    username: str,
    start_time: str,
    end_time: str,
    bot: str,
    current_user: Annotated[User, Depends(admin_plus)],
) -> User:
    """Allot a timeslot to the user
    Only root user is authorized to allot timeslots
    """

    # Check if the datetime string matches correct format
    try:
        datetime.strptime(start_time, "%y%m%d%H%M%S")
        datetime.strptime(end_time, "%y%m%d%H%M%S")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect datetime format, should be yymmddhhmmss",
        )

    user: User = ds.get_user(username)
    if user:
        ds.allot_timeslot(username, start_time, end_time, bot)
        return ds.get_user(username)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )