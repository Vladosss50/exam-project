import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database as db
import io
import sqlite3
import time

# ==================== НАСТРОЙКА ====================
st.set_page_config(page_title="Анализ продаж", layout="wide")

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
db.init_db()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# ==================== АВТОРИЗАЦИЯ ====================
def auth_page():
    st.title("🔐 Вход в систему")
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Имя пользователя")
            password = st.text_input("Пароль", type="password")
            submitted = st.form_submit_button("Войти")
            if submitted:
                user = db.login_user(username, password)
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.success("Вход выполнен!")
                    st.rerun()
                else:
                    st.error("Неверный логин или пароль")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Придумайте имя")
            new_password = st.text_input("Придумайте пароль", type="password")
            confirm_password = st.text_input("Подтвердите пароль", type="password")
            submitted = st.form_submit_button("Зарегистрироваться")
            if submitted:
                if new_password != confirm_password:
                    st.error("Пароли не совпадают!")
                elif len(new_password) < 4:
                    st.error("Пароль должен быть не менее 4 символов!")
                else:
                    if db.register_user(new_username, new_password):
                        st.success("Регистрация успешна! Теперь войдите.")
                    else:
                        st.error("Пользователь уже существует")

if st.session_state.user_id is None:
    auth_page()
    st.stop()

# ==================== ЗАГРУЗКА ФАЙЛА ====================
def process_file(uploaded_file):
    try:
        # Читаем файл
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Проверяем колонки
        required = ['date', 'category', 'product', 'quantity', 'price', 'city', 'manager']
        missing = [col for col in required if col not in df.columns]
        if missing:
            st.error(f"Отсутствуют колонки: {', '.join(missing)}")
            return None
        
        # Добавляем выручку
        df['revenue'] = df['quantity'] * df['price']
        
        # Сохраняем в БД
        conn = sqlite3.connect(db.DB_NAME)
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO sales (date, category, product, quantity, price, city, manager, revenue, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (row['date'], row['category'], row['product'], row['quantity'], 
                  row['price'], row['city'], row['manager'], row['revenue'], st.session_state.user_id))
        
        conn.commit()
        conn.close()
        
        st.success(f"✅ Загружено {len(df)} записей!")
        return df
    except Exception as e:
        st.error(f"Ошибка: {str(e)}")
        return None

# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================

# Заголовок
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <h1 style="color: white;">📊 Анализ продаж</h1>
        <p style="color: rgba(255,255,255,0.9);">Добро пожаловать, {st.session_state.username}!</p>
    </div>
""", unsafe_allow_html=True)

# Боковая панель
with st.sidebar:
    st.title("⚙️ Управление")
    
    if st.button("Выйти"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
    
    st.divider()
    
    # Загрузка файла
    st.header("📤 Загрузить данные")
    uploaded_file = st.file_uploader("Выберите файл", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        with st.spinner("Загрузка..."):
            process_file(uploaded_file)
        st.rerun()
    
    st.divider()
    
    # Фильтры
    df = db.get_data()
    
    st.header("🔍 Фильтры")
    
    categories = st.multiselect(
        "Категория",
        options=df['category'].unique(),
        default=df['category'].unique()
    )
    
    cities = st.multiselect(
        "Город",
        options=df['city'].unique(),
        default=df['city'].unique()
    )
    
    min_date = pd.to_datetime(df['date']).min().date()
    max_date = pd.to_datetime(df['date']).max().date()
    date_range = st.date_input("Период", value=(min_date, max_date))
    
    search = st.text_input("Поиск по товару")
    
    # Применяем фильтры
    filtered_df = df[
        (df['category'].isin(categories)) &
        (df['city'].isin(cities)) &
        (pd.to_datetime(df['date']).dt.date >= date_range[0]) &
        (pd.to_datetime(df['date']).dt.date <= date_range[1])
    ]
    
    if search:
        filtered_df = filtered_df[filtered_df['product'].str.contains(search, case=False)]

# Метрики
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Продажи", f"{len(filtered_df)} шт.")
with col2:
    st.metric("Выручка", f"{filtered_df['revenue'].sum():,.0f} ₽")
with col3:
    avg = filtered_df['revenue'].mean() if len(filtered_df) > 0 else 0
    st.metric("Средний чек", f"{avg:,.0f} ₽")
with col4:
    top = filtered_df.groupby('manager')['revenue'].sum().idxmax() if len(filtered_df) > 0 else "—"
    st.metric("Топ-менеджер", top)
with col5:
    total = filtered_df['quantity'].sum() if len(filtered_df) > 0 else 0
    st.metric("Товаров", f"{total} шт.")

st.divider()

# Кнопки
col_btn1, col_btn2, col_btn3 = st.columns(3)
with col_btn1:
    if st.button("➕ Добавить", use_container_width=True):
        st.session_state.show_add = not st.session_state.get("show_add", False)
with col_btn2:
    if st.button("🔄 Обновить", use_container_width=True):
        st.rerun()
with col_btn3:
    if st.button("📊 Статистика", use_container_width=True):
        st.session_state.show_stats = not st.session_state.get("show_stats", False)

# Форма добавления
if st.session_state.get("show_add", False):
    with st.expander("Новая продажа", expanded=True):
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("Дата")
                new_category = st.selectbox("Категория", df['category'].unique())
                new_product = st.text_input("Товар")
                new_quantity = st.number_input("Количество", min_value=1, step=1)
            with col2:
                new_price = st.number_input("Цена", min_value=1, step=100)
                new_city = st.selectbox("Город", df['city'].unique())
                new_manager = st.selectbox("Менеджер", df['manager'].unique())
            
            if st.form_submit_button("Сохранить"):
                if new_product:
                    db.add_sale(
                        new_date.strftime('%Y-%m-%d'), new_category, new_product,
                        new_quantity, new_price, new_city, new_manager,
                        st.session_state.user_id
                    )
                    st.success("Добавлено!")
                    st.session_state.show_add = False
                    st.rerun()

# Статистика
if st.session_state.get("show_stats", False) and len(filtered_df) > 0:
    with st.expander("Дополнительная статистика", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            top_products = filtered_df.groupby('product')['revenue'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(top_products.reset_index(), x='product', y='revenue', title='Топ-10 товаров')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            df_week = filtered_df.copy()
            df_week['weekday'] = pd.to_datetime(df_week['date']).dt.day_name()
            week_sales = df_week.groupby('weekday')['revenue'].sum().reset_index()
            fig = px.bar(week_sales, x='weekday', y='revenue', title='Продажи по дням недели')
            st.plotly_chart(fig, use_container_width=True)

# Графики
if len(filtered_df) > 0:
    tab1, tab2, tab3 = st.tabs(["Графики", "Таблица", "Экспорт"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(filtered_df.groupby('category')['revenue'].sum().reset_index(), 
                        x='category', y='revenue', title='Выручка по категориям')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.pie(filtered_df.groupby('category')['revenue'].sum().reset_index(), 
                        names='category', values='revenue', title='Доля категорий')
            st.plotly_chart(fig, use_container_width=True)
        
        fig = px.line(filtered_df.groupby('date')['revenue'].sum().reset_index(), 
                     x='date', y='revenue', title='Динамика продаж', markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        fig = px.bar(filtered_df.groupby('manager')['revenue'].sum().reset_index().sort_values('revenue', ascending=False),
                    x='manager', y='revenue', title='Рейтинг менеджеров')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.dataframe(filtered_df[['date', 'category', 'product', 'quantity', 'price', 'city', 'manager', 'revenue']], 
                    use_container_width=True)
    
    with tab3:
        csv = filtered_df.to_csv(index=False)
        st.download_button("Скачать CSV", data=csv, file_name=f"report_{datetime.now().strftime('%Y%m%d')}.csv")
else:
    st.warning("Нет данных для выбранных фильтров")

# Подвал
st.divider()
st.markdown(f"""
    <div style="text-align: center; color: #888;">
        <p>Анализ продаж | {datetime.now().year}</p>
        <p style="font-size: 12px;">Пользователь: {st.session_state.username} | Записей: {len(df)}</p>
    </div>
""", unsafe_allow_html=True)