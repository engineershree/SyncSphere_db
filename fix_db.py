import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fix_enum():
    try:
        # Connect to the PostgreSQL database
        db_url = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_TK6syMf9nUPq@ep-dark-salad-aqa2l1wl-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
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
