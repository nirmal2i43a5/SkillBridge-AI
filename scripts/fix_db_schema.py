import sqlite3
import os

def fix_schema():
    db_path = "jobs.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Nothing to fix.")
        return

    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Fix Jobs Table
    try:
        cursor.execute("SELECT min_years_experience FROM jobs LIMIT 1")
        print("Column 'min_years_experience' exists in 'jobs'.")
    except sqlite3.OperationalError:
        print("Column 'min_years_experience' missing in 'jobs'. Adding it...")
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN min_years_experience FLOAT DEFAULT 0.0")
            conn.commit()
            print("Added 'min_years_experience' to 'jobs'.")
        except Exception as e:
            print(f"Failed to alter 'jobs' table: {e}")

    # 2. Fix Candidates Table
    try:
        cursor.execute("SELECT total_years_experience FROM candidates LIMIT 1")
        print("Column 'total_years_experience' exists in 'candidates'.")
    except sqlite3.OperationalError:
        print("Column 'total_years_experience' missing in 'candidates'. Adding it...")
        try:
            cursor.execute("ALTER TABLE candidates ADD COLUMN total_years_experience FLOAT DEFAULT 0.0")
            conn.commit()
            print("Added 'total_years_experience' to 'candidates'.")
        except Exception as e:
            print(f"Failed to alter 'candidates' table: {e}")

    conn.close()
    print("Schema check complete.")

if __name__ == "__main__":
    fix_schema()
