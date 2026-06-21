import os

db_path = "c:\\Users\\SHRI\\Desktop\\SyncSphere_db\\syncsphere.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print("Deleted old syncsphere.db")
else:
    print("syncsphere.db not found")
