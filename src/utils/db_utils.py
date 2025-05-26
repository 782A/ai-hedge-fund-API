import mysql.connector
import os

def get_db_connection():
    """Establishes and returns a MySQL connection object."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB_NAME")
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def execute_query(query, params=None, connection=None, commit=False, fetchone=False, fetchall=False):
    """
    Executes an SQL query.

    Args:
        query (str): The SQL query string.
        params (tuple, optional): Parameters for the query. Defaults to None.
        connection (mysql.connector.connection_cext.CMySQLConnection, optional): Existing DB connection. Defaults to None.
        commit (bool, optional): Whether to commit the transaction. Defaults to False.
        fetchone (bool, optional): Whether to fetch one row. Defaults to False.
        fetchall (bool, optional): Whether to fetch all rows. Defaults to False.

    Returns:
        The result of fetch operation or cursor.lastrowid if applicable.
    """
    own_connection = False
    if connection is None:
        connection = get_db_connection()
        if connection is None:
            return None
        own_connection = True

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True if fetchone or fetchall else False) # Use dictionary cursor for fetch operations
        cursor.execute(query, params)

        if commit:
            connection.commit()
            return cursor.lastrowid

        if fetchone:
            return cursor.fetchone()

        if fetchall:
            return cursor.fetchall()
        
        return cursor # Should not happen if flags are used correctly, but as a fallback

    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        # TODO: Add more specific error handling or logging if needed
        return None
    finally:
        if cursor:
            cursor.close()
        if own_connection and connection and connection.is_connected():
            connection.close()
