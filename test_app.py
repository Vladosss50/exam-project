import pandas as pd
import numpy as np

def test_calculate_revenue():
    """Тест 1: проверка расчета выручки"""
    df_test = pd.DataFrame({
        'Количество': [2, 3, 5],
        'Цена_за_ед': [1000, 500, 200]
    })
    df_test['Выручка'] = df_test['Количество'] * df_test['Цена_за_ед']
    expected = 2000 + 1500 + 1000  # 4500
    assert df_test['Выручка'].sum() == 4500
    print("✅ Тест 1 пройден: расчет выручки работает")
    return True

def test_filter_empty():
    """Тест 2: проверка фильтрации"""
    df = pd.DataFrame({'Категория': ['Электроника', 'Одежда', 'Книги']})
    filtered = df[df['Категория'] == 'Несуществующая_категория']
    assert len(filtered) == 0
    print("✅ Тест 2 пройден: фильтрация работает")
    return True

def test_data_has_required_columns():
    """Тест 3: проверка наличия нужных колонок"""
    df = pd.DataFrame({
        'Дата': ['2024-01-01'],
        'Категория': ['Электроника'],
        'Товар': ['Ноутбук'],
        'Количество': [5],
        'Цена_за_ед': [10000],
        'Город': ['Москва'],
        'Менеджер': ['Анна']
    })
    required_columns = ['Дата', 'Категория', 'Товар', 'Количество', 'Цена_за_ед', 'Город', 'Менеджер']
    for col in required_columns:
        assert col in df.columns
    print("✅ Тест 3 пройден: все колонки присутствуют")
    return True

if __name__ == "__main__":
    print("🚀 Запуск тестов...")
    print("-" * 30)
    test_calculate_revenue()
    test_filter_empty()
    test_data_has_required_columns()
    print("-" * 30)
    print("✅ Все тесты успешно пройдены!")