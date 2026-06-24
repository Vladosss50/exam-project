import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database as db

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(page_title="Анализ продаж", layout="wide")

# Инициализация БД
db.init_db()

# ==================== АВТОРИЗАЦИЯ ====================
def auth_page():
    st.title("🔐 Вход в систему")
    
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        username = st.text_input("Имя пользователя", key="login_user")
        password = st.text_input("Пароль", type="password", key="login_pass")
        if st.button("Войти"):
            user = db.login_user(username, password)
            if user:
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.rerun()
            else:
                st.error("Неверный логин или пароль")
    
    with tab2:
        new_username = st.text_input("Придумайте имя", key="reg_user")
        new_password = st.text_input("Придумайте пароль", type="password", key="reg_pass")
        if st.button("Зарегистрироваться"):
            if db.register_user(new_username, new_password):
                st.success("Регистрация успешна! Теперь войдите.")
            else:
                st.error("Пользователь с таким именем уже существует")

# Проверка авторизации
if "user_id" not in st.session_state:
    auth_page()
    st.stop()

# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================
st.sidebar.title(f"👋 Привет, {st.session_state.username}!")
st.sidebar.write("---")

# Кнопка выхода
if st.sidebar.button("🚪 Выйти"):
    del st.session_state.user_id
    del st.session_state.username
    st.rerun()

st.title("📊 Анализ продаж интернет-магазина")

# Загрузка данных
df = db.get_data()

# ==================== ФИЛЬТРЫ ====================
st.sidebar.header("🔍 Фильтры")

categories = st.sidebar.multiselect(
    "Категория",
    options=df['category'].unique(),
    default=df['category'].unique()
)

cities = st.sidebar.multiselect(
    "Город",
    options=df['city'].unique(),
    default=df['city'].unique()
)

date_col = pd.to_datetime(df['date'])
min_date = date_col.min().date()
max_date = date_col.max().date()
date_range = st.sidebar.date_input(
    "Период",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

search_term = st.sidebar.text_input("🔎 Поиск по товару")

# Применение фильтров
filtered_df = df[
    (df['category'].isin(categories)) &
    (df['city'].isin(cities)) &
    (pd.to_datetime(df['date']).dt.date >= date_range[0]) &
    (pd.to_datetime(df['date']).dt.date <= date_range[1])
]

if search_term:
    filtered_df = filtered_df[filtered_df['product'].str.contains(search_term, case=False)]

# ==================== СВОДКА ====================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Всего продаж", f"{len(filtered_df)} шт.")
with col2:
    st.metric("💰 Общая выручка", f"{filtered_df['revenue'].sum():,.0f} ₽")
with col3:
    st.metric("📈 Средний чек", f"{filtered_df['revenue'].mean():,.0f} ₽" if len(filtered_df) > 0 else "Нет данных")
with col4:
    if len(filtered_df) > 0:
        top_manager = filtered_df.groupby('manager')['revenue'].sum().idxmax()
        st.metric("🏆 Топ-менеджер", top_manager)
    else:
        st.metric("🏆 Топ-менеджер", "Нет данных")

st.divider()

# ==================== ГРАФИКИ ====================
if len(filtered_df) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(
            filtered_df.groupby('category')['revenue'].sum().reset_index(),
            x='category', y='revenue', color='category',
            title='Выручка по категориям', color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.pie(
            filtered_df.groupby('category')['revenue'].sum().reset_index(),
            names='category', values='revenue',
            title='Доля категорий', color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Динамика
    daily_sales = filtered_df.groupby('date')['revenue'].sum().reset_index()
    fig3 = px.line(
        daily_sales, x='date', y='revenue',
        title='📈 Динамика продаж по дням', markers=True,
        color_discrete_sequence=['#2E86AB']
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Топ-менеджеры
    manager_sales = filtered_df.groupby('manager')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
    fig4 = px.bar(
        manager_sales, x='manager', y='revenue', color='manager',
        title='🏅 Рейтинг менеджеров', color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("⚠️ Нет данных для выбранных фильтров")

# ==================== ТАБЛИЦА ====================
st.subheader("📋 Детальные данные")

# Кнопки управления
col_actions1, col_actions2, col_actions3 = st.columns([1, 1, 4])

with col_actions1:
    if st.button("➕ Добавить запись"):
        st.session_state.show_add_form = True

with col_actions2:
    if st.button("🔄 Обновить данные"):
        st.rerun()

# Форма добавления
if st.session_state.get("show_add_form", False):
    with st.expander("📝 Новая продажа", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            new_date = st.date_input("Дата", datetime.now())
            new_category = st.selectbox("Категория", df['category'].unique())
            new_product = st.text_input("Товар")
            new_quantity = st.number_input("Количество", min_value=1, step=1)
        with col2:
            new_price = st.number_input("Цена за ед.", min_value=1, step=100)
            new_city = st.selectbox("Город", df['city'].unique())
            new_manager = st.selectbox("Менеджер", df['manager'].unique())
        
        if st.button("💾 Сохранить"):
            if new_product:
                db.add_sale(
                    new_date.strftime('%Y-%m-%d'), new_category, new_product,
                    new_quantity, new_price, new_city, new_manager,
                    st.session_state.user_id
                )
                st.success("✅ Запись добавлена!")
                st.session_state.show_add_form = False
                st.rerun()
            else:
                st.error("❌ Введите название товара")

# Таблица
if len(filtered_df) > 0:
    # Пагинация
    items_per_page = 10
    total_pages = (len(filtered_df) - 1) // items_per_page + 1
    page = st.number_input("Страница", min_value=1, max_value=total_pages, value=1, step=1)
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_data = filtered_df.iloc[start_idx:end_idx]
    
    st.dataframe(
        page_data[['date', 'category', 'product', 'quantity', 'price', 'city', 'manager', 'revenue']],
        use_container_width=True,
        column_config={
            "date": "Дата",
            "category": "Категория",
            "product": "Товар",
            "quantity": "Кол-во",
            "price": st.column_config.NumberColumn("Цена", format="%.0f ₽"),
            "city": "Город",
            "manager": "Менеджер",
            "revenue": st.column_config.NumberColumn("Выручка", format="%.0f ₽")
        },
        height=400
    )
    
    st.caption(f"Всего записей: {len(filtered_df)}")
    
    # Скачивание
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Скачать CSV",
        data=csv,
        file_name=f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.warning("⚠️ Нет данных")