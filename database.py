import sqlite3

def get_db_connection():
    # conn now equals sql connecting to the db 
    conn = sqlite3.connect('uss_events.db')
    conn.row_factory = sqlite3.Row
    return conn # conn is just a shorter way of saying connection 

def init_db():
    conn = get_db_connection() 
    
    # Creates the users table with role support if it doesn't already exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            dob TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    
    # Creates the events table matching your organiser form inputs
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room TEXT NOT NULL,
            created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    conn.commit() # once changes are made, commit them
    conn.close()

# Automatically build the database tables when initialized
init_db()