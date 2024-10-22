# Author: Ujwal N K
# Created On:
# Core functionality for the server - login, jwt, role-level access

from ..database import operations as ds

from datetime import datetime, timedelta, timezone, date

from fastapi import APIRouter, HTTPException, Depends, status, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext

from .schema import Token, TokenData, User, UserInDB
import sqlite3

from typing import Annotated

router = APIRouter()

with open("/etc/secret") as f:
    global SECRET_KEY
    SECRET_KEY = f.readline().strip()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

############### Role levels ###############

ROLE_DEVELOPER = "developer"
ROLE_ROOT = "root"
ROLE_ADMIN = "admin"

# Super User group, has access to all api endpoints
wheel_group = (ROLE_ROOT, ROLE_DEVELOPER)

# Admin has access only to managing api endpoints
admin_group = wheel_group + (ROLE_ADMIN,)

############### Role levels ###############


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    user_dict = ds.get_user_in_db(username)
    return UserInDB(**user_dict.dict())


def authenticate_user(username: str, password: str):
    user: UserInDB = ds.get_user_in_db(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    print("Returning user")
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode: dict = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        # Check username registered
        if username is None:
            raise credentials_exception

        # Allow only one user, check jwt against stored jwt
        elif (username not in admin_group) and (ds.get_jwt(username)[0] != token):
            # On multiple users using same account, remove the older login
            ds.set_jwt(username, None)
            raise credentials_exception

        token_data = TokenData(username=username)

    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    elif (current_user.username not in admin_group) and (
        (
            int(current_user.start_time) > int(datetime.now().strftime("%y%m%d%H%M%S"))
            or int(current_user.end_time) < int(datetime.now().strftime("%y%m%d%H%M%S"))
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Wait your turn",
                "timeslot_start": current_user.start_time,
                "timeslot_end": current_user.end_time,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


async def only_root_user(current_user: Annotated[User, Depends(get_current_user)]):
    """Allow only root user to access functionality"""
    if current_user.username not in wheel_group:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def only_developer(current_user: Annotated[User, Depends(get_current_user)]):
    "Allow only developer access functionality"
    if current_user.username != ROLE_DEVELOPER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="Developer only endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def admin_plus(current_user: Annotated[User, Depends(get_current_user)]):
    "Allow admin, root & developer to access endpoint"
    if current_user.username not in admin_group:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="Developer, root & admin endpoint only",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def iot_bot_access(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Allow only root user and user with timeslot alloted to iot_bot to access"""

    if current_user.bot == "iot" or current_user.username in wheel_group:
        return current_user

    elif current_user.bot == "ros":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are alloted a timeslot for ROS Bot",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def ros_bot_access(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Allow only root user and user with timeslot alloted to ros_bot to access"""
    if current_user.bot == "ros" or current_user.username in wheel_group:
        return current_user

    elif current_user.bot == "iot":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are alloted a timeslot for IOT Bot",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response_model=None
):

    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif user.disabled or user.blacklist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif (user.username not in admin_group) and (
        (
            int(user.start_time) > int(datetime.now().strftime("%y%m%d%H%M%S"))
            or int(user.end_time) < int(datetime.now().strftime("%y%m%d%H%M%S"))
        )
    ):

        print(
            int(user.start_time),
            int(user.end_time),
            int(datetime.now().strftime("%y%m%d%H%M%S")),
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Wait your turn",
                "timeslot_start": user.start_time,
                "timeslot_end": user.end_time,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Store token data in database
    ds.set_jwt(user.username, access_token)

    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/adduser/{username}",
    responses={
        401: {"description": "Only root user has the permission to create other users"},
        403: {"description": "Username already exists in the database"},
    },
)
async def add_user(
    user: UserInDB,
    current_user: Annotated[User, Depends(admin_plus)],
) -> User:
    """
    Create a new User(
        username (str): Username, must be unique for every user
        diabled (bool): Disable a user
        blacklist (bool): Blacklist a user for short duration
        date_of_birth (str): User date of birth for setting password
    )

    return: User
    """

    # Set a static past date (Oct 03, 2024) the date when this was implemented
    datetime_const = datetime(2024, 10, 3, 12, 30).strftime("%y%m%d%H%M%S")

    # Implemented to ensure no logins are possible before the initial timeslot allotement takes place
    user.start_time = datetime_const
    user.end_time = datetime_const

    # Set bot to null str
    user.bot = ""

    # Security feature to not allow the root to change the password on entry
    user.hashed_password = get_password_hash(user.username)
    try:
        ds.add_user(user)
        return ds.get_user_in_db(user.username)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Duplicate username",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/password/set",
    responses={
        200: {"description": "OK"},
        401: {"description": "User not authenticated, or using wrong username"},
        403: {"description": "Forbidden, cannot change root user password"},
    },
)
async def set_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    username: str,
    password: str,
    date_of_birth: date,
) -> User:
    """
    Allow user to set password

    param: User, password, date_of_birth

    return:
        - success: username
        - failure: HTTPException
    """

    if username in admin_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Allowed to change the admin password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Root user with the date of birth
    if (current_user in admin_group) and (
        ds.get_user(username).date_of_birth == date_of_birth
    ):
        user: User = ds.get_user(username)
        flag: User | None = ds.change_password(
            user.username, get_password_hash(password)
        )
        if flag:
            return flag
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Non-root user with the same username and date of birth
    elif (
        (current_user not in admin_group)
        and (current_user.username == user.username)
        and (user.date_of_birth == date_of_birth)
    ):
        user: User = ds.get_user(username)
        flag: User | None = ds.change_password(
            user.username, get_password_hash(password)
        )
        if flag:
            return flag
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    responses={
        401: {"description": "User not authenticated"},
        403: {"description": "Bot unallocated"},
        200: {"description": "OK"},
    },
)
async def get_username(current_user: Annotated[User, Depends(get_current_active_user)]):
    """

    Get the authenticated user, associated bot, and allocated timeslot
    Raise HTTP Exception incase bot not allocated


    @return
        {
            "username": username,
            "bot: associated bot,
            "start_time": Allocated time slot start
            "end_time": Allocated time slot end
        }

    """

    if current_user.username in admin_group:
        return {"username": current_user.username, "bot": "*", "start_time": None, "end_time": None}

    else:
        try:
            user: User = ds.get_user(current_user.username)

            return {
                "username": user.username,
                "bot": user.bot,
                "start_time": user.start_time,
                "end_time": user.end_time,
            }

        except:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No bot or timeslot allocated",
                headers={"WWW-Authenticate": "Bearer"},
            )


@router.get("/blacklist")
async def blacklist_user(current_user: Annotated[User, Depends(admin_plus)], username: str, status: bool):
    """
    Blacklist a user

    param: username

    return: username
    """
    return False
    return ds.blacklist_user(current_user.username, status)


@router.get("/disable_user")
async def disable_user(current_user: Annotated[User, Depends(only_root_user)], username:str, status: bool):
    """
    Disable / Enable a user

    param: username

    return: status of the user
    """
    return False
    return ds.disable_user(current_user.username, status)