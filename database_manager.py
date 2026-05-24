import sqlite3
import os

DB_NAME = "cozy_home.db"

def initialize_database():
    """
    Creates a secure local database file and builds the foundational 
    tables needed to run The COZY Home ecosystem.
    """
    print(f"🛠️ Connecting to database engine: {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. PARENT TABLE (Stores master household administrator profiles)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parents (
        parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # 2. CHILD TABLE (Stores gamified profile attributes for each child)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS children (
        child_id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER,
        first_name TEXT NOT NULL,
        age INTEGER,
        learning_interest TEXT DEFAULT 'General',
        points_balance INTEGER DEFAULT 0,
        avatar_equipped TEXT DEFAULT 'default_hero.png',
        FOREIGN KEY (parent_id) REFERENCES parents (parent_id)
    )""")

    # 3. QUESTS TABLE (Tracks household chores and homeschooling lessons as active tasks)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quests (
        quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER,
        assigned_to_child_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        points_reward INTEGER NOT NULL,
        category TEXT CHECK(category IN ('Chore', 'Homeschool', 'Behavior')),
        status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Submitted', 'Approved')),
        FOREIGN KEY (parent_id) REFERENCES parents (parent_id),
        FOREIGN KEY (assigned_to_child_id) REFERENCES children (child_id)
    )""")

    # 4. REWARDS SHOP TABLE (Stores items children can purchase with earned points)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rewards_shop (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_id INTEGER,
        item_name TEXT NOT NULL,
        cost_in_points INTEGER NOT NULL,
        stock_count INTEGER DEFAULT -1, -- -1 means infinite stock
        FOREIGN KEY (parent_id) REFERENCES parents (parent_id)
    )""")

    conn.commit()
    print("✅ Database tables successfully created!")

    # --- POPULATE INITIAL DEMO DATA FOR REAL-WORLD TESTING ---
    # Check if we already have data; if not, populate it so the app can spin up immediately
    cursor.execute("SELECT COUNT(*) FROM parents")
    if cursor.fetchone()[0] == 0:
        print("🌱 Seeding production sandbox with initial test profiles...")
        
        # Insert a default test parent profile
        cursor.execute("""
        INSERT INTO parents (first_name, email, password_hash) 
        VALUES ('Sarah', 'sarah@cozyhome.com', 'secure_hashed_password_123')
        """)
        parent_id = cursor.lastrowid

        # Insert two children with distinct customization preferences
        cursor.execute("""
        INSERT INTO children (parent_id, first_name, age, learning_interest, points_balance, avatar_equipped)
        VALUES (?, 'Tane', 8, 'Space Rockets', 150, 'rocket_captain.png')
        """, (parent_id,))
        
        cursor.execute("""
        INSERT INTO children (parent_id, first_name, age, learning_interest, points_balance, avatar_equipped)
        VALUES (?, 'Mia', 6, 'Magical Animals', 45, 'unicorn_princess.png')
        """, (parent_id,))
        child_2_id = cursor.lastrowid

        # Insert an active household chore/quest assigned to Mia
        cursor.execute("""
        INSERT INTO quests (parent_id, assigned_to_child_id, title, description, points_reward, category, status)
        VALUES (?, ?, 'Clean the Playroom', 'Organize all toy boxes and sweep the rug.', 20, 'Chore', 'Pending')
        """, (parent_id, child_2_id))

        # Insert a customized reward option into the family marketplace shop
        cursor.execute("""
        INSERT INTO rewards_shop (parent_id, item_name, cost_in_points)
        VALUES (?, '30 Minutes Video Game Time', 50)
        """, (parent_id,))

        conn.commit()
        print("🎉 Demo data injection complete.")

    conn.close()

if __name__ == "__main__":
    initialize_database()