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
    
    # Добавляем демо-данные, если таблица пустая
    cursor.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] == 0:
        insert_demo_data(cursor)
    
    conn.commit()
    conn.close()

def insert_demo_data(cursor):
    """Заполняет таблицу демо-данными"""
    categories = ['Электроника', 'Одежда', 'Книги', 'Дом', 'Спорт']
    products = {
        'Электроника': ['Ноутбук', 'Телефон', 'Наушники', 'Планшет'],
        'Одежда': ['Футболка', 'Джинсы', 'Куртка', 'Кроссовки'],
        'Книги': ['Роман', 'Учебник', 'Компьютерная литература', 'Детектив'],
        'Дом': ['Посуда', 'Мебель', 'Декор', 'Текстиль'],
        'Спорт': ['Мяч', 'Гантели', 'Коврик', 'Велосипед']
    }
    cities = ['Москва', 'СПб', 'Казань', 'Новосибирск', 'Екатеринбург']
    managers = ['Анна', 'Иван', 'Ольга', 'Петр', 'Мария']
    
    for i in range(50):
        date = datetime(2024, 1, 1) + timedelta(days=i)
        cat = random.choice(categories)
        prod = random.choice(products[cat])
        qty = random.randint(1, 20)
        price = round(random.uniform(500, 15000), 0)
        revenue = qty * price
        
        cursor.execute('''
            INSERT INTO sales (date, category, product, quantity, price, city, manager, revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date.strftime('%Y-%m-%d'), cat, prod, qty, price, random.choice(cities), random.choice(managers), revenue))

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

def update_sale(id, date, category, product, quantity, price, city, manager):
    """Обновляет продажу"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    revenue = quantity * price
    cursor.execute('''
        UPDATE sales SET date=?, category=?, product=?, quantity=?, price=?, city=?, manager=?, revenue=?
        WHERE id=?
    ''', (date, category, product, quantity, price, city, manager, revenue, id))
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