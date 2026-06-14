import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fix_enum():
    try:
        # Connect to the PostgreSQL database
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("Error: DATABASE_URL environment variable is not set in environment or .env file.")
            return
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Add the 'INTERN' value to the Postgres ENUM type
        cur.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'INTERN';")
        
        print("Success! 'INTERN' has been added to the Postgres database ENUM.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fix_enum()
