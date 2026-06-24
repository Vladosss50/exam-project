# Экзаменационный проект - анализ продаж
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(page_title="Анализ продаж", layout="wide")
st.title("📊 Анализ продаж интернет-магазина")

# ==================== ГЕНЕРАЦИЯ ДАННЫХ ====================
@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 50
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(n)]
    categories = ['Электроника', 'Одежда', 'Книги', 'Дом', 'Спорт']
    products = {
        'Электроника': ['Ноутбук', 'Телефон', 'Наушники', 'Планшет'],
        'Одежда': ['Футболка', 'Джинсы', 'Куртка', 'Кроссовки'],
        'Книги': ['Роман', 'Учебник', 'Компьютерная литература', 'Детектив'],
        'Дом': ['Посуда', 'Мебель', 'Декор', 'Текстиль'],
        'Спорт': ['Мяч', 'Гантели', 'Коврик', 'Велосипед']
    }
    
    data = []
    for i in range(n):
        cat = np.random.choice(categories)
        prod = np.random.choice(products[cat])
        data.append({
            'Дата': dates[i],
            'Категория': cat,
            'Товар': prod,
            'Количество': np.random.randint(1, 20),
            'Цена_за_ед': round(np.random.uniform(500, 15000), 0),
            'Город': np.random.choice(['Москва', 'СПб', 'Казань', 'Новосибирск', 'Екатеринбург']),
            'Менеджер': np.random.choice(['Анна', 'Иван', 'Ольга', 'Петр', 'Мария'])
        })
    df = pd.DataFrame(data)
    df['Выручка'] = df['Количество'] * df['Цена_за_ед']
    return df

df = generate_data()

# ==================== БОКОВОЕ МЕНЮ ====================
st.sidebar.header("🔍 Фильтры")

# Фильтр по категории
categories = st.sidebar.multiselect(
    "Категория",
    options=df['Категория'].unique(),
    default=df['Категория'].unique()
)

# Фильтр по городу
cities = st.sidebar.multiselect(
    "Город",
    options=df['Город'].unique(),
    default=df['Город'].unique()
)

# Фильтр по дате
min_date = df['Дата'].min().date()
max_date = df['Дата'].max().date()
date_range = st.sidebar.date_input(
    "Период",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Поиск по товару
search_term = st.sidebar.text_input("🔎 Поиск по товару")

# Применяем фильтры
filtered_df = df[
    (df['Категория'].isin(categories)) &
    (df['Город'].isin(cities)) &
    (df['Дата'] >= pd.to_datetime(date_range[0])) &
    (df['Дата'] <= pd.to_datetime(date_range[1]))
]

if search_term:
    filtered_df = filtered_df[filtered_df['Товар'].str.contains(search_term, case=False)]

# ==================== ОСНОВНОЙ КОНТЕНТ ====================

# Сводка
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Всего продаж", f"{len(filtered_df)} шт.")
with col2:
    st.metric("💰 Общая выручка", f"{filtered_df['Выручка'].sum():,.0f} ₽")
with col3:
    st.metric("📈 Средний чек", f"{filtered_df['Выручка'].mean():,.0f} ₽")
with col4:
    if len(filtered_df) > 0:
        top_manager = filtered_df.groupby('Менеджер')['Выручка'].sum().idxmax()
        st.metric("🏆 Топ-менеджер", top_manager)
    else:
        st.metric("🏆 Топ-менеджер", "Нет данных")

st.divider()

# ==================== ГРАФИК 1: Выручка по категориям ====================
st.subheader("📊 Выручка по категориям")
col1, col2 = st.columns(2)

with col1:
    if len(filtered_df) > 0:
        fig1 = px.bar(
            filtered_df.groupby('Категория')['Выручка'].sum().reset_index(),
            x='Категория',
            y='Выручка',
            color='Категория',
            title='Выручка по категориям'
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Нет данных для отображения")

with col2:
    if len(filtered_df) > 0:
        fig2 = px.pie(
            filtered_df.groupby('Категория')['Выручка'].sum().reset_index(),
            names='Категория',
            values='Выручка',
            title='Доля категорий'
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Нет данных для отображения")

# ==================== ГРАФИК 2: Динамика продаж ====================
st.subheader("📈 Динамика продаж по дням")
if len(filtered_df) > 0:
    daily_sales = filtered_df.groupby('Дата')['Выручка'].sum().reset_index()
    fig3 = px.line(
        daily_sales,
        x='Дата',
        y='Выручка',
        title='Ежедневная выручка',
        markers=True
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Нет данных для отображения")

# ==================== ГРАФИК 3: Топ-менеджеры ====================
st.subheader("🏅 Рейтинг менеджеров")
if len(filtered_df) > 0:
    manager_sales = filtered_df.groupby('Менеджер')['Выручка'].sum().reset_index().sort_values('Выручка', ascending=False)
    fig4 = px.bar(
        manager_sales,
        x='Менеджер',
        y='Выручка',
        color='Менеджер',
        title='Выручка по менеджерам'
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Нет данных для отображения")

# ==================== ТАБЛИЦА ДАННЫХ ====================
st.subheader("📋 Детальные данные")
if len(filtered_df) > 0:
    st.dataframe(
        filtered_df.style.format({
            'Цена_за_ед': '{:,.0f} ₽',
            'Выручка': '{:,.0f} ₽'
        }),
        use_container_width=True,
        height=300
    )
else:
    st.warning("⚠️ Нет данных, соответствующих выбранным фильтрам. Измените параметры фильтрации.")

# ==================== СОХРАНЕНИЕ РЕЗУЛЬТАТОВ ====================
st.subheader("💾 Сохранить результаты")

col1, col2 = st.columns(2)
with col1:
    if len(filtered_df) > 0:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Скачать CSV",
            data=csv,
            file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.button("📥 Скачать CSV", disabled=True)

with col2:
    if st.button("🔄 Сбросить фильтры"):
        st.rerun()