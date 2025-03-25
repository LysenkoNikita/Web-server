import sqlite3
import os
import datetime
import base64

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends

from Tables import createTables

app = FastAPI()

def convert_to_binary_data(filename):
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data

def write_to_file(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)
    print("Данный из blob сохранены в: ", filename, "\n")

"""Проверка данных таблиц"""
def get_db():
    conn = sqlite3.connect('game_database.db', check_same_thread=False)
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.close()

def initialize_database():
    conn = sqlite3.connect('game_database.db', check_same_thread=False)
    cursor = conn.cursor()
    createTables(cursor)
    conn.close()

initialize_database()

origins = [
    "http://localhost:3000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

"""Авторизация"""
@app.post("/auth")
def auth(data: dict, cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute('SELECT id, name, mail FROM Users WHERE mail = ? AND password = ?', (data['email'], data["password"]))
    existing_user = cursor.fetchone()

    if existing_user:
        return {"id":existing_user[0], "email": existing_user[2], "username": existing_user[1]}
    else:
        raise HTTPException(status_code=403, detail="Неверный логин или пароль")

"""Регистрация"""
@app.post("/signup")
def signup(data: dict, cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute('SELECT id FROM Users WHERE mail = ?', (data['email'],))
    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=403, detail="Пользователь с таким email уже существует")
    else:
        cursor.execute('''
            INSERT INTO Users (name, mail, password, isEditor, isAdmin)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['username'], data['email'], data['password'], data.get('isEditor', False), data.get('isAdmin', False)))

        cursor.connection.commit()

        cursor.execute('SELECT id, name, mail FROM Users WHERE mail = ? AND password = ?',
                       (data['email'], data["password"]))
        existing_user = cursor.fetchone()

        return {"id": existing_user[0], "email": existing_user[2], "username": existing_user[1]}

@app.get("/get_users")
def get_users(cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute('SELECT id, mail, password FROM Users')
    users = cursor.fetchall()
    return users

@app.get("/get_games")
def get_users(cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute('SELECT id FROM Games')
    games = cursor.fetchall()
    print(games)
    return games

@app.post("/createGame")
async def create_game(
    title: str=Form(...),
    genre: str=Form(...),
    studio: str=Form(...),
    year: str=Form(...),
    description: str=Form(...),
    link: str=Form(...),
    image: UploadFile = File(...),
    cursor: sqlite3.Cursor = Depends(get_db)
):
        image_data = await image.read()

        image_base64 = f"data:{image.content_type};base64," + base64.b64encode(image_data).decode('utf-8')

        cursor.execute('SELECT id FROM Games WHERE name = ? AND studio = ?', (title, studio))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Игра уже существует")

        cursor.execute('''
            INSERT INTO Games (name, genre, studio, year, img, description, link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, genre, studio, year, image_base64, description, link))
        cursor.connection.commit()

        return {"message": "Игра успешно добавлена"}


@app.get("/home/")
async def get_page(
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(10, le=100, description="Элементов на странице"),
        cursor: sqlite3.Cursor = Depends(get_db)
):
    cursor.execute('SELECT COUNT(*) FROM Games')
    total_games = cursor.fetchone()[0]
    total_pages = (total_games + per_page - 1) // per_page

    offset = (page - 1) * per_page
    cursor.execute(
        'SELECT id, name, img, description FROM Games LIMIT ? OFFSET ?',
        (per_page, offset)
    )
    games = cursor.fetchall()

    return {
        "games": [{"id": g[0], "name": g[1], "image": g[2], "description": g[3]} for g in games],
        "totalPages": total_pages,
        "currentPage": page,
        "perPage": per_page,
        "totalGames": total_games
    }

@app.get("/games/{id}")
async def get_game(id:str, cursor: sqlite3.Cursor = Depends(get_db)):
    cursor.execute("SELECT id, name, genre, studio, year, img, description, link FROM Games WHERE id = ?", (id))
    game = cursor.fetchone()
    return {
        "id": game[0],
        "name": game[1],
        "genre": game[2],
        "studio": game[3],
        "year": game[4],
        "img": game[5],
        "description": game[6],
        "link": game[7]
    }