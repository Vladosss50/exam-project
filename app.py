import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import database as db
import io

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(
    page_title="Анализ продаж", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ТЕМА ОФОРМЛЕНИЯ ====================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# ==================== CSS ДЛЯ КРАСИВОГО ОФОРМЛЕНИЯ ====================
def apply_css():
    if st.session_state.theme == "dark":
        st.markdown("""
            <style>
                .stApp { background-color: #0e1117; color: #fafafa; }
                .stMetric { background-color: #1e1e2e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
                .stDataFrame { background-color: #1e1e2e; }
                .stButton > button { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 8px 24px; }
                .stSelectbox, .stTextInput, .stDateInput { background-color: #1e1e2e; }
                .stTabs [data-baseweb="tab-list"] { background-color: #1e1e2e; border-radius: 10px; }
                .stTabs [data-baseweb="tab"] { color: #fafafa; }
                .sidebar .sidebar-content { background-color: #1a1a2e; }
                .main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 30px; }
                h1, h2, h3 { color: #fafafa !important; }
                .stExpander { background-color: #1e1e2e; border-radius: 10px; border: 1px solid #333; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
                .stButton > button { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 8px 24px; transition: transform 0.2s; }
                .stButton > button:hover { transform: scale(1.05); }
                .stTabs [data-baseweb="tab-list"] { background-color: #f8f9fa; border-radius: 10px; }
                .main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; margin-bottom: 30px; }
                .main-header h1 { color: white !important; }
                .stExpander { border-radius: 10px; border: 1px solid #e9ecef; }
                .stAlert { border-radius: 10px; }
            </style>
        """, unsafe_allow_html=True)

# ==================== ИНИЦИАЛИЗАЦИЯ БД ====================
db.init_db()

# ==================== АВТОРИЗАЦИЯ ====================
def auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://img.icons8.com/fluency/96/null/data-configuration.png", width=80)
        st.title("🔐 Вход в систему")
        
        # Переключатель темы на странице входа
        theme_col1, theme_col2 = st.columns([3, 1])
        with theme_col2:
            if st.button("🌓" if st.session_state.theme == "light" else "☀️"):
                toggle_theme()
                st.rerun()
        
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
    apply_css()
    auth_page()
    st.stop()

# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================
apply_css()

# Заголовок с аватаркой
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1>📊 Анализ продаж интернет-магазина</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 0;">Добро пожаловать, {st.session_state.username}! 👋</p>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; color: white;">⚡ {datetime.now().strftime('%d.%m.%Y %H:%M')}</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==================== БОКОВАЯ ПАНЕЛЬ ====================
with st.sidebar:
    st.title("⚙️ Управление")
    
    col_theme, col_logout = st.columns(2)
    with col_theme:
        if st.button("🌓" if st.session_state.theme == "light" else "☀️", help="Переключить тему"):
            toggle_theme()
            st.rerun()
    with col_logout:
        if st.button("🚪 Выйти", help="Выйти из аккаунта"):
            del st.session_state.user_id
            del st.session_state.username
            st.rerun()
    
    st.divider()
    
    # Загрузка данных
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
    
    # Применение фильтров
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
    st.metric("📦 Продажи", f"{len(filtered_df)} шт.", delta=None)
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
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns([1, 1, 1, 1, 6])

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
            # Топ-товары
            top_products = filtered_df.groupby('product')['revenue'].sum().sort_values(ascending=False).head(10)
            fig_top = px.bar(
                top_products.reset_index(),
                x='product', y='revenue',
                title='🏆 Топ-10 товаров по выручке',
                color_discrete_sequence=['#667eea']
            )
            st.plotly_chart(fig_top, use_container_width=True)
        with col2:
            # Продажи по дням недели
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
        
        # Динамика
        daily_sales = filtered_df.groupby('date')['revenue'].sum().reset_index()
        fig3 = px.line(
            daily_sales, x='date', y='revenue',
            title='📈 Динамика продаж',
            markers=True,
            color_discrete_sequence=['#667eea']
        )
        fig3.update_layout(xaxis_title="Дата", yaxis_title="Выручка (₽)")
        st.plotly_chart(fig3, use_container_width=True)
        
        # Топ-менеджеры
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
        
        # Пагинация
        items_per_page = 10
        total_pages = max(1, (len(filtered_df) - 1) // items_per_page + 1)
        page = st.number_input("📄 Страница", min_value=1, max_value=total_pages, value=1, step=1, key="page_num")
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_data = filtered_df.iloc[start_idx:end_idx]
        
        # Красивая таблица
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
        
        # Удаление записи
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
            # CSV
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📄 Скачать CSV",
                data=csv,
                file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_exp2:
            # Excel
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
st.markdown(
    f"""
    <div style="text-align: center; color: #888; padding: 20px 0;">
        <p>📊 Анализ продаж интернет-магазина | Сделано с ❤️ | {datetime.now().year}</p>
        <p style="font-size: 12px;">Пользователь: {st.session_state.username} | Всего записей: {len(df)}</p>
    </div>
    """,
    unsafe_allow_html=True
)