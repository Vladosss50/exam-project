import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database as db
import io
import os

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(
    page_title="Анализ продаж", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ДЛЯ СВЕТЛОЙ ТЕМЫ ====================
st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff;
        }
        
        .stMetric {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* ========== КНОПКИ С ОТСТУПАМИ ========== */
        div[data-testid="column"] {
            padding-right: 15px !important;
            padding-left: 0px !important;
        }
        div[data-testid="column"]:last-child {
            padding-right: 0px !important;
        }
        
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            transition: all 0.2s ease;
            white-space: nowrap;
            width: 100%;
            min-width: 120px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 500;
            margin: 0 !important;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
        }
        
        .stButton > button:hover {
            transform: scale(1.03);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.5);
            background: linear-gradient(90deg, #7b93f5 0%, #8b5fbf 100%);
        }
        
        .stButton > button:active {
            transform: scale(0.97);
            box-shadow: 0 1px 2px rgba(102, 126, 234, 0.2);
        }
        
        .sidebar .stButton > button {
            width: 100%;
            min-width: unset;
            padding: 8px 12px;
            font-size: 13px;
        }
        
        form .stButton > button {
            min-width: 100px;
            padding: 8px 24px;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f8f9fa;
            border-radius: 10px;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .main-header h1 {
            color: white !important;
        }
        .main-header p {
            color: rgba(255,255,255,0.9) !important;
        }
        .header-time {
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            white-space: nowrap;
        }
        
        .stExpander {
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        
        .stAlert {
            border-radius: 10px;
        }
        
        .stSidebar {
            background-color: #f8f9fa;
        }
        .stSidebar .stTitle {
            color: #333;
        }
        
        .stDataFrame {
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        
        .footer {
            text-align: center;
            color: #888;
            padding: 20px 0;
        }
        .footer p {
            margin: 5px 0;
        }
        
        .stSelectbox, .stTextInput, .stDateInput, .stNumberInput {
            background-color: white;
        }
        
        .stMarkdown, .stText, .stTitle, .stSubheader, .stHeader {
            color: #333333 !important;
        }
        
        .main-header h1, .main-header p, .main-header span {
            color: white !important;
        }
        
        .dataframe {
            background-color: white !important;
        }
        
        .stSidebar label {
            color: #333333 !important;
            font-weight: 500;
        }
        
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #333333 !important;
        }

        .upload-container {
            border: 2px dashed #667eea;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            background-color: #f8f9fa;
            margin-bottom: 20px;
        }
        .upload-container p {
            color: #667eea !important;
            font-size: 18px;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# ==================== ИНИЦИАЛИЗАЦИЯ БД ====================
db.init_db()

# ==================== ЗАГРУЗКА ФАЙЛА ====================
def load_uploaded_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("❌ Поддерживаются только CSV и Excel файлы!")
            return None
        
        required_columns = ['date', 'category', 'product', 'quantity', 'price', 'city', 'manager']
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ В файле отсутствуют колонки: {', '.join(missing_cols)}")
            st.info("💡 Требуемые колонки: date, category, product, quantity, price, city, manager")
            return None
        
        df['revenue'] = df['quantity'] * df['price']
        
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
        
        st.success(f"✅ Успешно загружено {len(df)} записей!")
        return df
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке файла: {str(e)}")
        return None

# ==================== АВТОРИЗАЦИЯ ====================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Вход в систему")
        
        tab1, tab2 = st.tabs(["🔑 Вход", "📝 Регистрация"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("👤 Имя пользователя", placeholder="Введите логин")
                password = st.text_input("🔒 Пароль", type="password", placeholder="Введите пароль")
                submitted = st.form_submit_button("🚀 Войти", use_container_width=True)
                if submitted:
                    user = db.login_user(username, password)
                    if user:
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.success("✅ Вход выполнен успешно!")
                        st.rerun()
                    else:
                        st.error("❌ Неверный логин или пароль")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("👤 Придумайте имя", placeholder="Введите логин")
                new_password = st.text_input("🔒 Придумайте пароль", type="password", placeholder="Введите пароль")
                confirm_password = st.text_input("✅ Подтвердите пароль", type="password", placeholder="Повторите пароль")
                submitted = st.form_submit_button("📝 Зарегистрироваться", use_container_width=True)
                if submitted:
                    if new_password != confirm_password:
                        st.error("❌ Пароли не совпадают!")
                    elif len(new_password) < 4:
                        st.error("❌ Пароль должен быть не менее 4 символов!")
                    else:
                        if db.register_user(new_username, new_password):
                            st.success("✅ Регистрация успешна! Теперь войдите.")
                        else:
                            st.error("❌ Пользователь с таким именем уже существует")

# Проверка авторизации
if "user_id" not in st.session_state:
    auth_page()
    st.stop()

# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================

# Заголовок
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1>📊 Анализ продаж интернет-магазина</h1>
                <p>Добро пожаловать, {st.session_state.username}! 👋</p>
            </div>
            <div>
                <span class="header-time">⚡ {datetime.now().strftime('%d.%m.%Y %H:%M')}</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==================== БОКОВАЯ ПАНЕЛЬ ====================
with st.sidebar:
    st.title("⚙️ Управление")
    
    if st.button("🚪 Выйти", use_container_width=True, help="Выйти из аккаунта"):
        del st.session_state.user_id
        del st.session_state.username
        st.rerun()
    
    st.divider()
    
    # Загрузка файла
    st.header("📤 Загрузить данные")
    
    st.markdown("""
        <div class="upload-container">
            <p>📂 Перетащите файл сюда</p>
            <p style="font-size: 12px; color: #888 !important;">Поддерживаются CSV и Excel (.xlsx, .xls)</p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Выберите файл",
        type=['csv', 'xlsx', 'xls'],
        label_visibility="collapsed",
        help="Загрузите файл с данными. Требуемые колонки: date, category, product, quantity, price, city, manager"
    )
    
    if uploaded_file is not None:
        with st.spinner("Загрузка данных..."):
            load_uploaded_file(uploaded_file)
        st.rerun()
    
    st.divider()
    
    # Фильтры
    df = db.get_data()
    
    st.header("🔍 Фильтры")
    
    categories = st.multiselect(
        "📂 Категория",
        options=df['category'].unique(),
        default=df['category'].unique()
    )
    
    cities = st.multiselect(
        "🌆 Город",
        options=df['city'].unique(),
        default=df['city'].unique()
    )
    
    date_col = pd.to_datetime(df['date'])
    min_date = date_col.min().date()
    max_date = date_col.max().date()
    date_range = st.date_input(
        "📅 Период",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    search_term = st.text_input("🔎 Поиск по товару", placeholder="Введите название...")
    
    filtered_df = df[
        (df['category'].isin(categories)) &
        (df['city'].isin(cities)) &
        (pd.to_datetime(df['date']).dt.date >= date_range[0]) &
        (pd.to_datetime(df['date']).dt.date <= date_range[1])
    ]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['product'].str.contains(search_term, case=False)]

# ==================== МЕТРИКИ ====================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📦 Продажи", f"{len(filtered_df)} шт.")
with col2:
    st.metric("💰 Выручка", f"{filtered_df['revenue'].sum():,.0f} ₽")
with col3:
    avg_check = filtered_df['revenue'].mean() if len(filtered_df) > 0 else 0
    st.metric("📈 Средний чек", f"{avg_check:,.0f} ₽")
with col4:
    if len(filtered_df) > 0:
        top_manager = filtered_df.groupby('manager')['revenue'].sum().idxmax()
        st.metric("🏆 Топ-менеджер", top_manager)
    else:
        st.metric("🏆 Топ-менеджер", "—")
with col5:
    total_products = filtered_df['quantity'].sum() if len(filtered_df) > 0 else 0
    st.metric("📦 Товаров", f"{total_products} шт.")

st.divider()

# ==================== КНОПКИ УПРАВЛЕНИЯ (С ОТСТУПАМИ) ====================
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1, 7])

with col_btn1:
    if st.button("➕ Добавить", use_container_width=True):
        st.session_state.show_add_form = not st.session_state.get("show_add_form", False)

with col_btn2:
    if st.button("🔄 Обновить", use_container_width=True):
        st.rerun()

with col_btn3:
    if st.button("📊 Статистика", use_container_width=True):
        st.session_state.show_stats = not st.session_state.get("show_stats", False)

# ==================== ФОРМА ДОБАВЛЕНИЯ ====================
if st.session_state.get("show_add_form", False):
    with st.expander("📝 Новая продажа", expanded=True):
        with st.form("add_sale_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("📅 Дата", datetime.now())
                new_category = st.selectbox("📂 Категория", df['category'].unique())
                new_product = st.text_input("📦 Товар", placeholder="Введите название товара")
                new_quantity = st.number_input("🔢 Количество", min_value=1, step=1, value=1)
            with col2:
                new_price = st.number_input("💰 Цена за ед.", min_value=1, step=100, value=1000)
                new_city = st.selectbox("🌆 Город", df['city'].unique())
                new_manager = st.selectbox("👨‍💼 Менеджер", df['manager'].unique())
            
            col_btn_submit, col_btn_cancel = st.columns(2)
            with col_btn_submit:
                submitted = st.form_submit_button("💾 Сохранить", use_container_width=True)
            with col_btn_cancel:
                if st.form_submit_button("❌ Отмена", use_container_width=True):
                    st.session_state.show_add_form = False
                    st.rerun()
            
            if submitted:
                if not new_product:
                    st.error("❌ Введите название товара!")
                else:
                    db.add_sale(
                        new_date.strftime('%Y-%m-%d'), new_category, new_product,
                        new_quantity, new_price, new_city, new_manager,
                        st.session_state.user_id
                    )
                    st.success("✅ Запись успешно добавлена!")
                    st.session_state.show_add_form = False
                    st.rerun()

# ==================== СТАТИСТИКА ====================
if st.session_state.get("show_stats", False) and len(filtered_df) > 0:
    with st.expander("📊 Дополнительная статистика", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            top_products = filtered_df.groupby('product')['revenue'].sum().sort_values(ascending=False).head(10)
            fig_top = px.bar(
                top_products.reset_index(),
                x='product', y='revenue',
                title='🏆 Топ-10 товаров по выручке',
                color_discrete_sequence=['#667eea']
            )
            st.plotly_chart(fig_top, use_container_width=True)
        with col2:
            df_weekday = filtered_df.copy()
            df_weekday['weekday'] = pd.to_datetime(df_weekday['date']).dt.day_name()
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_sales = df_weekday.groupby('weekday')['revenue'].sum().reindex(weekday_order).reset_index()
            fig_week = px.bar(
                weekday_sales,
                x='weekday', y='revenue',
                title='📅 Продажи по дням недели',
                color_discrete_sequence=['#764ba2']
            )
            st.plotly_chart(fig_week, use_container_width=True)

# ==================== ГРАФИКИ ====================
if len(filtered_df) > 0:
    tab1, tab2, tab3 = st.tabs(["📊 Графики", "📋 Таблица", "📥 Экспорт"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                filtered_df.groupby('category')['revenue'].sum().reset_index(),
                x='category', y='revenue',
                title='💰 Выручка по категориям',
                color='category',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.pie(
                filtered_df.groupby('category')['revenue'].sum().reset_index(),
                names='category', values='revenue',
                title='📊 Доля категорий',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        daily_sales = filtered_df.groupby('date')['revenue'].sum().reset_index()
        fig3 = px.line(
            daily_sales, x='date', y='revenue',
            title='📈 Динамика продаж',
            markers=True,
            color_discrete_sequence=['#667eea']
        )
        fig3.update_layout(xaxis_title="Дата", yaxis_title="Выручка (₽)")
        st.plotly_chart(fig3, use_container_width=True)
        
        manager_sales = filtered_df.groupby('manager')['revenue'].sum().reset_index().sort_values('revenue', ascending=False)
        fig4 = px.bar(
            manager_sales, x='manager', y='revenue',
            title='🏅 Рейтинг менеджеров',
            color='manager',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    
    with tab2:
        st.subheader("📋 Детальные данные")
        
        items_per_page = 10
        total_pages = max(1, (len(filtered_df) - 1) // items_per_page + 1)
        page = st.number_input("📄 Страница", min_value=1, max_value=total_pages, value=1, step=1, key="page_num")
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_data = filtered_df.iloc[start_idx:end_idx]
        
        st.dataframe(
            page_data[['id', 'date', 'category', 'product', 'quantity', 'price', 'city', 'manager', 'revenue']],
            use_container_width=True,
            column_config={
                "id": "ID",
                "date": "📅 Дата",
                "category": "📂 Категория",
                "product": "📦 Товар",
                "quantity": "🔢 Кол-во",
                "price": st.column_config.NumberColumn("💰 Цена", format="%.0f ₽"),
                "city": "🌆 Город",
                "manager": "👨‍💼 Менеджер",
                "revenue": st.column_config.NumberColumn("💰 Выручка", format="%.0f ₽")
            },
            height=400,
            hide_index=True
        )
        
        st.caption(f"📊 Всего записей: {len(filtered_df)} | Страница {page} из {total_pages}")
        
        st.subheader("🗑️ Управление записями")
        col_del1, col_del2 = st.columns([1, 4])
        with col_del1:
            delete_id = st.number_input("ID записи для удаления", min_value=1, step=1, key="delete_id")
        with col_del2:
            if st.button("🗑️ Удалить запись", use_container_width=True):
                if delete_id in filtered_df['id'].values:
                    db.delete_sale(delete_id)
                    st.success(f"✅ Запись #{delete_id} удалена!")
                    st.rerun()
                else:
                    st.error(f"❌ Запись #{delete_id} не найдена!")
    
    with tab3:
        st.subheader("📥 Экспорт данных")
        
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📄 Скачать CSV",
                data=csv,
                file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_exp2:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, sheet_name='Sales', index=False)
            st.download_button(
                label="📊 Скачать Excel",
                data=output.getvalue(),
                file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        st.info("💡 **Подсказка:** CSV подходит для открытия в любых программах, Excel — для профессиональной работы.")
        
else:
    st.warning("⚠️ Нет данных для выбранных фильтров. Попробуйте изменить параметры фильтрации.")

# ==================== ПОДВАЛ ====================
st.divider()
st.markdown(f"""
    <div class="footer">
        <p>📊 Анализ продаж интернет-магазина | Сделано с ❤️ | {datetime.now().year}</p>
        <p style="font-size: 12px;">Пользователь: {st.session_state.username} | Всего записей: {len(df)}</p>
    </div>
""", unsafe_allow_html=True)