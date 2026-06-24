import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================
st.set_page_config(
    page_title="Анализ продаж", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ====================
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
        
        /* ========== КНОПКИ В ОДНУ СТРОКУ С ОТСТУПАМИ ========== */
        .btn-container {
            display: flex;
            gap: 15px;
            flex-wrap: nowrap;
            align-items: center;
            margin-bottom: 10px;
        }
        .btn-container .stButton {
            flex: 0 0 auto;
        }
        .btn-container .stButton > button {
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
        .btn-container .stButton > button:hover {
            transform: scale(1.03);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.5);
            background: linear-gradient(90deg, #7b93f5 0%, #8b5fbf 100%);
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
    </style>
""", unsafe_allow_html=True)

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

# ==================== ЗАГОЛОВОК ====================
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1>📊 Анализ продаж интернет-магазина</h1>
                <p>Добро пожаловать! 👋</p>
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
    st.divider()
    
    st.header("🔍 Фильтры")
    
    categories = st.multiselect(
        "📂 Категория",
        options=df['Категория'].unique(),
        default=df['Категория'].unique()
    )
    
    cities = st.multiselect(
        "🌆 Город",
        options=df['Город'].unique(),
        default=df['Город'].unique()
    )
    
    search_term = st.text_input("🔎 Поиск по товару", placeholder="Введите название...")
    
    filtered_df = df[
        (df['Категория'].isin(categories)) &
        (df['Город'].isin(cities))
    ]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Товар'].str.contains(search_term, case=False)]

# ==================== МЕТРИКИ ====================
col1, col2, col3, col4, col5 = st.columns(5)

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
with col5:
    total_products = filtered_df['Количество'].sum() if len(filtered_df) > 0 else 0
    st.metric("📦 Товаров", f"{total_products} шт.")

st.divider()

# ==================== КНОПКИ УПРАВЛЕНИЯ (ЧЕРЕЗ HTML) ====================
st.markdown('<div class="btn-container">', unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    if st.button("➕ Добавить", use_container_width=True):
        st.session_state.show_add_form = not st.session_state.get("show_add_form", False)

with col_btn2:
    if st.button("🔄 Обновить", use_container_width=True):
        st.rerun()

with col_btn3:
    if st.button("📊 Статистика", use_container_width=True):
        st.session_state.show_stats = not st.session_state.get("show_stats", False)

st.markdown('</div>', unsafe_allow_html=True)

# ==================== ФОРМА ДОБАВЛЕНИЯ ====================
if st.session_state.get("show_add_form", False):
    with st.expander("📝 Новая продажа", expanded=True):
        with st.form("add_sale_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("📅 Дата", datetime.now())
                new_category = st.selectbox("📂 Категория", df['Категория'].unique())
                new_product = st.text_input("📦 Товар", placeholder="Введите название товара")
                new_quantity = st.number_input("🔢 Количество", min_value=1, step=1, value=1)
            with col2:
                new_price = st.number_input("💰 Цена за ед.", min_value=1, step=100, value=1000)
                new_city = st.selectbox("🌆 Город", df['Город'].unique())
                new_manager = st.selectbox("👨‍💼 Менеджер", df['Менеджер'].unique())
            
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
                    # Добавляем в DataFrame
                    new_row = pd.DataFrame({
                        'Дата': [new_date.strftime('%Y-%m-%d')],
                        'Категория': [new_category],
                        'Товар': [new_product],
                        'Количество': [new_quantity],
                        'Цена': [new_price],
                        'Город': [new_city],
                        'Менеджер': [new_manager],
                        'Выручка': [new_quantity * new_price]
                    })
                    global df
                    df = pd.concat([df, new_row], ignore_index=True)
                    st.success("✅ Запись успешно добавлена!")
                    st.session_state.show_add_form = False
                    st.rerun()

# ==================== СТАТИСТИКА ====================
if st.session_state.get("show_stats", False) and len(filtered_df) > 0:
    with st.expander("📊 Дополнительная статистика", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            top_products = filtered_df.groupby('Товар')['Выручка'].sum().sort_values(ascending=False).head(10)
            fig_top = px.bar(
                top_products.reset_index(),
                x='Товар', y='Выручка',
                title='🏆 Топ-10 товаров по выручке',
                color_discrete_sequence=['#667eea']
            )
            st.plotly_chart(fig_top, use_container_width=True)
        with col2:
            df_weekday = filtered_df.copy()
            df_weekday['День недели'] = pd.to_datetime(df_weekday['Дата']).dt.day_name()
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_sales = df_weekday.groupby('День недели')['Выручка'].sum().reindex(weekday_order).reset_index()
            fig_week = px.bar(
                weekday_sales,
                x='День недели', y='Выручка',
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
                filtered_df.groupby('Категория')['Выручка'].sum().reset_index(),
                x='Категория', y='Выручка',
                title='💰 Выручка по категориям',
                color='Категория',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.pie(
                filtered_df.groupby('Категория')['Выручка'].sum().reset_index(),
                names='Категория', values='Выручка',
                title='📊 Доля категорий',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        daily_sales = filtered_df.groupby('Дата')['Выручка'].sum().reset_index()
        fig3 = px.line(
            daily_sales, x='Дата', y='Выручка',
            title='📈 Динамика продаж',
            markers=True,
            color_discrete_sequence=['#667eea']
        )
        fig3.update_layout(xaxis_title="Дата", yaxis_title="Выручка (₽)")
        st.plotly_chart(fig3, use_container_width=True)
        
        manager_sales = filtered_df.groupby('Менеджер')['Выручка'].sum().reset_index().sort_values('Выручка', ascending=False)
        fig4 = px.bar(
            manager_sales, x='Менеджер', y='Выручка',
            title='🏅 Рейтинг менеджеров',
            color='Менеджер',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    
    with tab2:
        st.subheader("📋 Детальные данные")
        st.dataframe(filtered_df, use_container_width=True)
    
    with tab3:
        st.subheader("📥 Экспорт данных")
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Скачать CSV",
            data=csv,
            file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.info("💡 **Подсказка:** CSV подходит для открытия в любых программах.")
        
else:
    st.warning("⚠️ Нет данных для выбранных фильтров. Попробуйте изменить параметры фильтрации.")

# ==================== ПОДВАЛ ====================
st.divider()
st.markdown(f"""
    <div class="footer">
        <p>📊 Анализ продаж интернет-магазина | Сделано с ❤️ | {datetime.now().year}</p>
        <p style="font-size: 12px;">Всего записей: {len(df)}</p>
    </div>
""", unsafe_allow_html=True)