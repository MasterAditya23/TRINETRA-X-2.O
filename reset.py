import os
import sqlite3
import glob

print("⚠️  INITIATING CLEAN SLATE PROTOCOL ⚠️\n")

# 1. Clear Database
db_path = os.path.join("backend", "trinetra.db")
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM events")
        conn.commit()
        conn.close()
        print("✅ Event database wiped to 0.")
    except Exception as e:
        print(f"❌ Database error: {e}")
else:
    print("⚠️ Database not found, skipping...")

# 2. Clear Snapshots
snapshot_dir = os.path.join("data", "snapshots")
if os.path.exists(snapshot_dir):
    snapshots = glob.glob(os.path.join(snapshot_dir, "*.jpg"))
    for file in snapshots:
        try:
            os.remove(file)
        except Exception as e:
            print(f"❌ Failed to delete {file}: {e}")
    print(f"✅ Deleted {len(snapshots)} evidence snapshots.")
else:
    print("⚠️ Snapshot directory not found, skipping...")

print("\n🚀 TRINETRA X IS RESET AND READY FOR DEMO.")