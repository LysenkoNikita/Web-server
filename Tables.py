

def createTables(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mail TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        isEditor BOOLEAN DEFAULT FALSE,
        isAdmin BOOLEAN DEFAULT FALSE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        genre TEXT NOT NULL,
        studio TEXT NOT NULL,
        year INTEGER NOT NULL,
        img TEXT,
        description TEXT,
        link TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        datetime TEXT NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users(id),
        FOREIGN KEY (game_id) REFERENCES Games(id)
    )
    ''')
    cursor.connection.commit()
