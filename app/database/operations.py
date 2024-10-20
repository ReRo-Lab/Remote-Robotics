import sqlite3

from datetime import date
from typing import List

from ..core.schema import User, UserInDB


def add_user(user: UserInDB):
    """
    Function to add a new user into the database

    param: UserInDB
    return: bool (success)
    exceptions: sqlite3 Integrity error / sqlite3 Error / other
    """
    success_flag = False
    sqliteConnection = None
    
    try:
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
        cursor = sqliteConnection.cursor()
        print('DB Init')

        # Write a query to insert the user data into the table
        query = '''
        INSERT INTO users (username, hashed_password, disabled, blacklist, start_time, end_time, date_of_birth, bot, jwt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        # Execute the query with the user data
        cursor.execute(query, (user.username, user.hashed_password, user.disabled, user.blacklist, user.start_time, user.end_time, user.date_of_birth, user.bot, user.jwt))
        sqliteConnection.commit()
        
        print('User added successfully to the database.')

        # Close the cursor
        cursor.close()

        success_flag = True

    # Catch  integrity error - unique key repetition
    except sqlite3.IntegrityError as error:
        print('Unique key violation occurred -', error)
        raise sqlite3.IntegrityError

    # Catch other SQL errors
    except sqlite3.Error as error:
        print('Error occurred -', error)

    # General exception
    except Exception as e:
        print("Non SQL Exception -", e)

    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')

    return success_flag

def get_users() -> List[User]:
    
        users: List[User] = []
        sqliteConnection = None
    
        try:
            sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
            cursor = sqliteConnection.cursor()
            print('Connected to DB')
    
            # Write a query to fetch all the users
            query = "SELECT * FROM users"
            cursor.execute(query)
            users_details = cursor.fetchall()
    
            # Check if users exist
            if users_details:
                # Create a User object with the fetched details
                for user_details in users_details:
                    # TODO: Check why hash_password is being added???
                    user = User(username=user_details[0], hashed_password=user_details[1], disabled=user_details[2], blacklist=user_details[3], start_time=user_details[4], end_time=user_details[5], date_of_birth=user_details[6], bot=user_details[7])
                    users.append(user)
            else:
                print("DB: No users found")
            
        # Handle errors
        except sqlite3.Error as error:
            print('DB: Error occurred - ', error)
    
        
        except Exception as e:
            print("DB: Non SQL Exception -", e)
    
        finally:
    
            if sqliteConnection:
                sqliteConnection.close()
                print("DB: Connection Closed")

            print(users)
    
            return users


# TODO: Optimize this function to use get_user_in_db and remove the hashed_password
def get_user(username: str) -> User | None:

    user: User | None = None
    sqliteConnection = None

    try: 
        sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
        cursor = sqliteConnection.cursor()
        print('Connected to DB')

        # Write a query to fetch the user details based on the username
        query = "SELECT * FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        user_details = cursor.fetchone()

        # Check if user exists
        if user_details:
            # Create a User object with the fetched details
            # TODO: Check why hash_password is being added???
            user = UserInDB(username=user_details[0], hashed_password=user_details[1], disabled=user_details[2], blacklist=user_details[3], start_time=user_details[4], end_time=user_details[5], date_of_birth=user_details[6], bot=user_details[7], jwt=user_details[8])
            print(user, type(user))
        else:
            print("DB: User", username, "not found")
        
    # Handle errors
    except sqlite3.Error as error:
        print('DB: Error occurred - ', error)

    
    except Exception as e:
        print("DB: Non SQL Exception -", e)

    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print("DB: Connection Closed")

        return user


def get_user_in_db(username: str) -> UserInDB | None:

    user: User | None = None
    sqliteConnection = None

    try: 
        sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
        cursor = sqliteConnection.cursor()
        print('Connected to DB in get_user_in_db')

        # Write a query to fetch the user details based on the username
        query = "SELECT * FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        user_details = cursor.fetchone()

        # Check if user exists
        if user_details:
            # Create a User object with the fetched details
            user = UserInDB(username=user_details[0], hashed_password=user_details[1], disabled=user_details[2], blacklist=user_details[3], start_time=user_details[4], end_time=user_details[5], date_of_birth=user_details[6], bot=user_details[7], jwt=user_details[8])
            print(user, type(user))
        else:
            print("DB: User", username, "not found")
        
    # Handle errors
    except sqlite3.Error as error:
        print('DB: Error occurred - ', error)

    
    except Exception as e:
        print("DB: Non SQL Exception -", e)

    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print("DB: Connection Closed")

        return user

def set_jwt(username: str, jwt: str):
    """Store the user jwt token"""

    sqliteConnection = None

    try:
        sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
        cursor = sqliteConnection.cursor()
        print('DB: Init')

        # Update the jwt of the user
        query = "UPDATE users SET jwt = ? WHERE username = ?"
        cursor.execute(query, (jwt, username))
        sqliteConnection.commit()

        # Check if any rows were affected
        if cursor.rowcount > 0:
            print("DB: User", username, "jwt updated successfully")
        else:
            print("DB: User", username, "not found")
        
    # Handle errors
    except sqlite3.Error as error:
        print('DB: Error occurred - ', error)
        raise sqlite3.Error
    
    except Exception as e:
        print("DB: Non SQL Exception -", e)
        raise e

    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print("DB: Connection Closed")


def get_jwt(username):
    """Get the user jwt token"""

    jwt = None
    sqliteConnection = None

    try:
        sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
        cursor = sqliteConnection.cursor()
        print('DB: Init')

        # Write a query to fetch the jwt of the user
        query = "SELECT jwt FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        jwt = cursor.fetchone()

        # Check if jwt exists
        if jwt:
            print("DB: User", username, "jwt found")
        else:
            print("DB: User", username, "not found")
        
    # Handle errors
    except sqlite3.Error as error:
        print('DB: Error occurred - ', error)
        raise sqlite3.Error
    
    except Exception as e:
        print("DB: Non SQL Exception -", e)
        raise e

    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print("DB: Connection Closed")

        return jwt

def allot_timeslot(username: str, start_time: str, end_time: str, bot: str) -> User | None:
    
        sqliteConnection = None
        user = None
    
        try:
            sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
            cursor = sqliteConnection.cursor()
            print('DB: Init')
    
            # Update the start_time and end_time of the user
            query = "UPDATE users SET start_time = ?, end_time = ?, bot= ? WHERE username = ?"
            cursor.execute(query, (start_time, end_time, bot, username))
            sqliteConnection.commit()
    
            # Check if any rows were affected
            if cursor.rowcount > 0:
                print("DB: User", username, "timeslot updated successfully")
            else:
                print("DB: User", username, "not found")
            
        # Handle errors
        except sqlite3.Error as error:
            print('DB: Error occurred - ', error)
            raise sqlite3.Error
        
        except Exception as e:
            print("DB: Non SQL Exception -", e)
            raise e
    
        finally:
    
            if sqliteConnection:
                sqliteConnection.close()
                print("DB: Connection Closed")
    
            return user
        

def change_password(username: str, hashed_password: str) -> User | None:
    
        user = None
        sqliteConnection = None
    
        try:
            sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
            cursor = sqliteConnection.cursor()
            print('DB: Init')
    
            # Update the password of the user
            query = "UPDATE users SET hashed_password = ? WHERE username = ?"
            cursor.execute(query, (hashed_password, username))
            sqliteConnection.commit()
    
            # Check if any rows were affected
            if cursor.rowcount > 0:
                print("DB: User", username, "password updated successfully")
                user = get_user(username)
            else:
                print("DB: User", username, "not found")
                return None
            
        # Handle errors
        except sqlite3.Error as error:
            print('DB: Error occurred - ', error)
            raise sqlite3.Error
        
        except Exception as e:
            print("DB: Non SQL Exception -", e)
            raise e
    
        finally:
    
            if sqliteConnection:
                sqliteConnection.close()
                print("DB: Connection Closed")
    
            return user