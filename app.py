import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database as db
import io
import sqlite3
import time

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(
    page_title="Анализ продаж", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ====================
st.markdown("""
    <style>
        .stApp { background-color: #ffffff; }
        .stMetric {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 24px;
            transition: all 0.2s ease;
            white-space: nowrap;
            min-width: 130px;
            height: 40px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
            margin: 0 !important;
        }
        .stButton > button:hover {
            transform: scale(1.03);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.5);
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
        .main-header h1 { color: white !important; }
        .main-header p { color: rgba(255,255,255,0.9) !important; }
        .header-time {
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            white-space: nowrap;
        }
        .stExpander { border-radius: 10px; border: 1px solid #e9ecef; }
        .stAlert { border-radius: 10px; }
        .stSidebar { background-color: #f8f9fa; }
        .stSidebar .stTitle { color: #333; }
        .stDataFrame { border-radius: 10px; border: 1px solid #e9ecef; }
        .footer { text-align: center; color: #888; padding: 20px 0; }
        .footer p { margin: 5px 0; }
        .stSelectbox, .stTextInput, .stDateInput, .stNumberInput { background-color: white; }
        .stMarkdown, .stText, .stTitle, .stSubheader, .stHeader { color: #333333 !important; }
        .main-header h1, .main-header p, .main-header span { color: white !important; }
        .dataframe { background-color: white !important; }
        .stSidebar label { color: #333333 !important; font-weight: 500; }
        .stSidebar h1, .stSidebar h2, .stSidebar h3 { color: #333333 !important; }
        .upload-container {
            border: 2px dashed #667eea;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            background-color: #f8f9fa;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .upload-container:hover {
            border-color: #764ba2;
            background-color: #f0edff;
        }
        .upload-container p { color: #667eea !important; font-size: 18px; font-weight: 500; }
        .upload-container .sub-text { color: #888 !important; font-size: 12px; }
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .loader-text { color: #667eea !important; font-size: 16px; font-weight: 500; text-align: center; }
        .loader-subtext { color: #888 !important; font-size: 13px; text-align: center; }
        .progress-container {
            width: 100%;
            background-color: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-bar {
            height: 20px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 10px;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
db.init_db()

# Инициализация состояния загрузки
if "uploading" not in st.session_state:
    st.session_state.uploading = False
if "upload_complete" not in st.session_state:
    st.session_state.upload_complete = False
if "upload_message" not in st.session_state:
    st.session_state.upload_message = ""

# ==================== ЗАГРУЗКА ФАЙЛА ====================
def load_uploaded_file_with_progress(uploaded_file):
    """Загружает файл с отображением прогресса"""
    try:
        st.session_state.uploading = True
        st.session_state.upload_complete = False
        
        start_time = time.time()
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        # Шаг 1: Чтение файла
        status_placeholder.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div class="loader"></div>
                <p class="loader-text">⏳ Чтение файла...</p>
                <p class="loader-subtext">Пожалуйста, подождите</p>
            </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(20)
        time.sleep(0.3)
        
        # Чтение файла
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("❌ Поддерживаются только CSV и Excel файлы!")
            st.session_state.uploading = False
            return None
        
        # Шаг 2: Проверка данных
        status_placeholder.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div class="loader"></div>
                <p class="loader-text">🔍 Проверка данных...</p>
                <p class="loader-subtext">Проверяем структуру файла</p>
            </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(40)
        time.sleep(0.3)
        
        required_columns = ['date', 'category', 'product', 'quantity', 'price', 'city', 'manager']
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ В файле отсутствуют колонки: {', '.join(missing_cols)}")
            st.info("💡 Требуемые колонки: date, category, product, quantity, price, city, manager")
            st.session_state.uploading = False
            return None
        
        # Шаг 3: Обработка
        status_placeholder.markdown("""
            <div style="text-align: center; padding: 20px;">
                <div class="loader"></div>
                <p class="loader-text">📊 Обработка данных...</p>
                <p class="loader-subtext">Рассчитываем выручку</p>
            </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(60)
        time.sleep(0.3)
        
        df['revenue'] = df['quantity'] * df['price']
        
        # Шаг 4: Сохранение в БД
        status_placeholder.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <div class="loader"></div>
                <p class="loader-text">💾 Сохранение в базу данных...</p>
                <p class="loader-subtext">Записываем {len(df):,} записей</p>
            </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(80)
        
        conn = sqlite3.connect(db.DB_NAME)
        cursor = conn.cursor()
        
        total_rows = len(df)
        batch_size = 500
        
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            for _, row in batch.iterrows():
                cursor.execute('''
                    INSERT INTO sales (date, category, product, quantity, price, city, manager, revenue, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['date'], row['category'], row['product'], row['quantity'], 
                      row['price'], row['city'], row['manager'], row['revenue'], st.session_state.user_id))
            
            current_progress = 80 + (i + len(batch)) / total_rows * 20
            progress_bar.progress(min(int(current_progress), 99))
        
        conn.commit()
        conn.close()
        
        progress_bar.progress(100)
        status_placeholder.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <p style="color: #28a745 !important; font-size: 48px;">✅</p>
                <p class="loader-text" style="color: #28a745 !important;">Загрузка завершена!</p>
                <p class="loader-subtext">Добавлено {len(df):,} записей за {time.time() - start_time:.1f} секунд</p>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(0.5)
        
        st.session_state.upload_complete = True
        st.session_state.uploading = False
        st.session_state.upload_message = f"✅ Успешно загружено {len(df)} записей!"
        
        return df
        
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке файла: {str(e)}")
        st.session_state.uploading = False
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
        # Сбрасываем состояние загрузки
        st.session_state.uploading = False
        st.session_state.upload_complete = False
        del st.session_state.user_id
        del st.session_state.username
        st.rerun()
    
    st.divider()
    
    # Загрузка файла
    st.header("📤 Загрузить данные")
    
    st.markdown("""
        <div class="upload-container">
            <p>📂 Перетащите файл сюда</p>
            <p class="sub-text">Поддерживаются CSV и Excel (.xlsx, .xls)</p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Выберите файл",
        type=['csv', 'xlsx', 'xls'],
        label_visibility="collapsed",
        help="Загрузите файл с данными. Требуемые колонки: date, category, product, quantity, price, city, manager",
        key="file_uploader"
    )
    
    # Проверяем, нужно ли загружать файл
    if uploaded_file is not None and not st.session_state.upload_complete:
        load_uploaded_file_with_progress(uploaded_file)
        st.rerun()
    
    # Показываем сообщение об успешной загрузке
    if st.session_state.upload_complete and st.session_state.upload_message:
        st.success(st.session_state.upload_message)
        # Сбрасываем флаг после отображения
        if st.button("🔄 Сбросить состояние загрузки"):
            st.session_state.upload_complete = False
            st.session_state.upload_message = ""
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

# ==================== КНОПКИ УПРАВЛЕНИЯ ====================
col_btn1, col_btn2, col_btn3 = st.columns(3)

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