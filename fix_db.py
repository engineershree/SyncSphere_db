import psycopg2

def fix_enum():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect("postgresql://postgres:root@localhost:5432/SyncSphere")
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
