import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    # We temporarily connect to the default 'neondb' database on the same Neon host to create 'syncsphere_db'
    base_url = "postgresql://neondb_owner:npg_TK6syMf9nUPq@ep-dark-salad-aqa2l1wl-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to default 'neondb' database to provision 'syncsphere_db'...")
        conn = psycopg2.connect(base_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname='syncsphere_db';")
        exists = cur.fetchone()
        
        if not exists:
            print("Database 'syncsphere_db' does not exist. Provisioning database on Neon...")
            cur.execute("CREATE DATABASE syncsphere_db;")
            print("SUCCESS: Database 'syncsphere_db' successfully created on Neon!")
        else:
            print("Database 'syncsphere_db' already exists on your Neon account.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"ERROR: Error provisioning database: {e}")

if __name__ == "__main__":
    create_database()
