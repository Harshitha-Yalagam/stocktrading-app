import sqlite3 
conn = sqlite3.connect("database.db") 
cursor = conn.cursor() 
cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, hash TEXT NOT NULL, cash REAL DEFAULT 10000.0)""") 
cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, symbol TEXT NOT NULL, shares INTEGER NOT NULL, price REAL NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id))""") 
conn.commit() 
conn.close() 
print("Database and tables created successfully!") 
