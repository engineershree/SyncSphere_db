import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
db_url = os.getenv("DATABASE_URL")

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT id, email, first_name, is_deleted FROM users;")
users = cur.fetchall()

print(f"Found {len(users)} users in the database:")
for u in users:
    print(u)
cur.close()
conn.close()
