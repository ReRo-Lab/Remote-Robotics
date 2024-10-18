from datetime import datetime, date
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class User(BaseModel):
    """
    User class
    
    username: Userid, unique id
    blacklist: blacklisted user
    disabled: disabled user
    start_time: start time of the user timeslot for access
    stop_time: end time of the user timeslot for access
    date_of_birth: User date of birth
    bot: Bot access during the timeslot
    """

    username: str
    blacklist: bool = False
    disabled : bool = False
    start_time: str
    end_time: str
    date_of_birth: date
    bot: str


class UserInDB(User):
    """
    UserInDB(User) Class 
    
    hashed_password: Password string hashed
    jwt: jwt token last associated with user
    """
    hashed_password: str
    jwt: str