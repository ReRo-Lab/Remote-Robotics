import sqlite3

from datetime import date
from typing import List

from ..core.schema import User, UserInDB

def init():
    sqliteConnection = None

    try:
        sqliteConnection = sqlite3.connect("/var/lib/sqlite/users.db")
        cursor = sqliteConnection.cursor()
        print('DB: Init')

        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = cursor.fetchone()

        if table_exists:
            # Write a query and execute it with cursor
            query = 'select sqlite_version();'
            cursor.execute(query)
        else:
            print('Table does not exist.')         
            
            # Create the table
            create_table_query = '''
            CREATE TABLE users (
                username TEXT PRIMARY KEY,
                hashed_password TEXT NOT NULL,
                disabled BOOL NOT NULL,
                blacklist BOOL NOT NULL,
                start_time TEXT,
                end_time TEXT,
                date_of_birth DATE,
                bot TEXT,
                jwt TEXT
            );
            '''

            cursor.execute(create_table_query)
            sqliteConnection.commit()
            print('Table created successfully.')

            def add_top_level_user(values):

                # Insert root user into the table
                query = '''
                INSERT INTO users (username, hashed_password, disabled, blacklist, start_time, end_time, date_of_birth, bot, jwt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                # Execute the query with the user data
                cursor.execute(query, values)

                sqliteConnection.commit()

            # Add the root user
            add_top_level_user(("root", '$2b$12$7GcEqfDu5/.Kfrtsd0r68OAEcp2kMiyNDbba95aosOkrN5laurui2', 0, 0, 0, 0, date(year=2024, month=10, day=10), "", ""))
            print('DB: Root user created successfully.')

            # Add the developer
            add_top_level_user(("developer", '$2b$12$XrlrGZEcqcBgjtI09Xaz0edKKfay7VklOXtcMWFxN1c8fOWQRdkHa', 0, 0, 0, 0, date(year=2024, month=10, day=10), "", ""))
            print('DB: Developer created successfully.')

            # Add the admin user
            add_top_level_user(("admin", '$2b$12$f4SAGmDqVhHurbiGM/D.mOc1zLtvNM9JQTjPMH/JkjsP2KIWUN5aC', 0, 0, 0, 0, date(year=2024, month=10, day=10), "", ""))
            print('DB: Admin created successfully.')

    # Handle errors
    except sqlite3.Error as error:
        print('DB: Error occurred - ', error)

    
    except Exception as e:
        print("DB: Non SQL Exception -", e)

    finally:

        if sqliteConnection:
            sqliteConnection.close()
            print('DB: SQLite Connection closed')



init()