import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from the .env file
load_dotenv()

# Retrieve the database credentials from environment variables
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

try:
    # Establish a connection to the database
    connection = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )

    # Create a cursor object using the connection
    cursor = connection.cursor()

    # Execute a query to retrieve all rows from the dummy_table
    cursor.execute("SELECT * FROM dummy_table;")

    # Fetch all rows from the result of the query
    rows = cursor.fetchall()

    # Print the results
    for row in rows:
        print(row)

    # Close the cursor and connection
    cursor.close()
    connection.close()

except Exception as e:
    print(f"Error connecting to the PostgreSQL database: {e}")