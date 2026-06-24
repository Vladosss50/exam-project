import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

# Настройка страницы
st.set_page_config(page_title="Анализ продаж", layout="wide")

# Заголовок
st.title("📊 Анализ продаж интернет-магазина")

# ==================== ГЕНЕРАЦИЯ ДАННЫХ ====================
@st.cache_data
def generate_data():
    categories = ['Электроника', 'Одежда', 'Книги', 'Дом', 'Спорт']
    products = {
        'Электроника': ['Ноутбук', 'Телефон', 'Наушники', 'Планшет'],
        'Одежда': ['Футболка', 'Джинсы', 'Куртка', 'Кроссовки'],
        'Книги': ['Роман', 'Учебник', 'Детектив', 'Фантастика'],
        'Дом': ['Посуда', 'Мебель', 'Декор', 'Текстиль'],
        'Спорт': ['Мяч', 'Гантели', 'Коврик', 'Велосипед']
    }
    cities = ['Москва', 'СПб', 'Казань', 'Новосибирск', 'Екатеринбург']
    managers = ['Анна', 'Иван', 'Ольга', 'Петр', 'Мария']
    
    data = []
    for i in range(50):
        date = datetime(2024, 1, 1) + timedelta(days=i)
        cat = random.choice(categories)
        prod = random.choice(products[cat])
        qty = random.randint(1, 20)
        price = round(random.uniform(500, 15000), 0)
        data.append({
            'Дата': date.strftime('%Y-%m-%d'),
            'Категория': cat,
            'Товар': prod,
            'Количество': qty,
            'Цена': price,
            'Город': random.choice(cities),
            'Менеджер': random.choice(managers),
            'Выручка': qty * price
        })
    return pd.DataFrame(data)

df = generate_data()

# ==================== БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ ====================
st.sidebar.header("🔍 Фильтры")

categories = st.sidebar.multiselect(
    "Категория",
    options=df['Категория'].unique(),
    default=df['Категория'].unique()
)

cities = st.sidebar.multiselect(
    "Город",
    options=df['Город'].unique(),
    default=df['Город'].unique()
)

search_term = st.sidebar.text_input("🔎 Поиск по товару")

# Применяем фильтры
filtered_df = df[
    (df['Категория'].isin(categories)) &
    (df['Город'].isin(cities))
]

if search_term:
    filtered_df = filtered_df[filtered_df['Товар'].str.contains(search_term, case=False)]

# ==================== МЕТРИКИ ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Продажи", f"{len(filtered_df)} шт.")
with col2:
    st.metric("💰 Выручка", f"{filtered_df['Выручка'].sum():,.0f} ₽")
with col3:
    avg_check = filtered_df['Выручка'].mean() if len(filtered_df) > 0 else 0
    st.metric("📈 Средний чек", f"{avg_check:,.0f} ₽")
with col4:
    if len(filtered_df) > 0:
        top_manager = filtered_df.groupby('Менеджер')['Выручка'].sum().idxmax()
        st.metric("🏆 Топ-менеджер", top_manager)
    else:
        st.metric("🏆 Топ-менеджер", "—")

st.divider()

# ==================== ГРАФИКИ ====================
if len(filtered_df) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(
            filtered_df.groupby('Категория')['Выручка'].sum().reset_index(),
            x='Категория', y='Выручка',
            title='💰 Выручка по категориям',
            color='Категория'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.pie(
            filtered_df.groupby('Категория')['Выручка'].sum().reset_index(),
            names='Категория', values='Выручка',
            title='📊 Доля категорий'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Динамика продаж
    daily_sales = filtered_df.groupby('Дата')['Выручка'].sum().reset_index()
    fig3 = px.line(
        daily_sales, x='Дата', y='Выручка',
        title='📈 Динамика продаж',
        markers=True
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Рейтинг менеджеров
    manager_sales = filtered_df.groupby('Менеджер')['Выручка'].sum().reset_index().sort_values('Выручка', ascending=False)
    fig4 = px.bar(
        manager_sales, x='Менеджер', y='Выручка',
        title='🏅 Рейтинг менеджеров',
        color='Менеджер'
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # ==================== ТАБЛИЦА ====================
    st.subheader("📋 Детальные данные")
    st.dataframe(filtered_df, use_container_width=True)
    
    # ==================== СКАЧИВАНИЕ ====================
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Скачать CSV",
        data=csv,
        file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
else:
    st.warning("⚠️ Нет данных для выбранных фильтров")

# ==================== ПОДВАЛ ====================
st.divider()
st.markdown(
    f"""
    <div style="text-align: center; color: #888; padding: 10px;">
        <p>📊 Анализ продаж интернет-магазина | {datetime.now().year}</p>
    </div>
    """,
    unsafe_allow_html=True
)