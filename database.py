import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

DB_NAME = "sales.db"

def init_db():
    """Создает таблицы, если их нет"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица продаж
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            city TEXT NOT NULL,
            manager TEXT NOT NULL,
            revenue REAL NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_data():
    """Возвращает все данные из БД в виде DataFrame"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM sales ORDER BY date DESC", conn)
    conn.close()
    return df

def add_sale(date, category, product, quantity, price, city, manager, user_id):
    """Добавляет новую продажу"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    revenue = quantity * price
    cursor.execute('''
        INSERT INTO sales (date, category, product, quantity, price, city, manager, revenue, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, category, product, quantity, price, city, manager, revenue, user_id))
    conn.commit()
    conn.close()

def delete_sale(id):
    """Удаляет продажу"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales WHERE id=?", (id,))
    conn.commit()
    conn.close()

def register_user(username, password):
    """Регистрирует нового пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def login_user(username, password):
    """Проверяет логин пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user