"""
Главный модуль приложения для анализа транзакций.
Запускает все реализованные функциональности проекта.
"""

import os
import pandas as pd
from views import main_page
from services import simple_search
from reports import spending_by_category


def create_sample_data() -> pd.DataFrame:
    """
    Создает пример данных для демонстрации, если файл не найден.

    Returns:
        DataFrame с тестовыми транзакциями
    """
    print("Создание тестовых данных для демонстрации...")

    sample_data = {
        'Дата операции': [
            '2021-12-01', '2021-12-05', '2021-12-10', '2021-12-15',
            '2021-12-20', '2021-11-01', '2021-11-05', '2021-11-10',
            '2021-10-01', '2021-10-10'
        ],
        'Сумма операции': [
            100.50, 250.75, 50.25, 300.00, 75.30, 200.00,
            150.00, 80.00, 120.00, 90.00
        ],
        'Номер карты': [
            '1234567812345678', '1234567812345678', '8765432187654321',
            '1234567812345678', '8765432187654321', '1234567812345678',
            '8765432187654321', '1234567812345678', '8765432187654321',
            '1234567812345678'
        ],
        'Категория': [
            'Продукты', 'Супермаркеты', 'Транспорт', 'Супермаркеты',
            'Кафе', 'Продукты', 'Транспорт', 'Супермаркеты',
            'Продукты', 'Транспорт'
        ],
        'Описание': [
            'Покупка в магазине', 'Супермаркет Лента', 'Такси до работы',
            'Супермаркет Ашан', 'Кофе с коллегами', 'Продукты на неделю',
            'Общественный транспорт', 'Супермаркет Перекресток',
            'Овощи и фрукты', 'Метро'
        ]
    }

    return pd.DataFrame(sample_data)


def load_transactions() -> pd.DataFrame:
    """
    Загружает транзакции из Excel-файла.
    Если файл не найден, создает тестовые данные.

    Returns:
        DataFrame с транзакциями
    """
    try:
        # Исправляем путь к файлу - поднимаемся на уровень выше из src
        file_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'operations.xlsx'
        )
        absolute_path = os.path.abspath(file_path)

        print(f"Попытка загрузки файла: {absolute_path}")

        if not os.path.exists(absolute_path):
            print(f"Файл {absolute_path} не найден. Создание тестовых данных...")
            return create_sample_data()

        df = pd.read_excel(absolute_path)
        print(f"Успешно загружено {len(df)} транзакций из {absolute_path}")
        return df
    except Exception as e:
        print(f"Ошибка при загрузке транзакций: {e}")
        return create_sample_data()


def main():
    """
    Главная функция приложения.
    Запускает все реализованные функциональности.
    """
    print("Запуск анализатора транзакций...")

    df = load_transactions()

    # Показываем информацию о данных
    print(f"Загружено {len(df)} транзакций")
    print("Колонки в данных:", list(df.columns))
    print("Первые 3 транзакции:")
    print(df.head(3))

    # Преобразование в список словарей для сервисов
    transactions = df.to_dict('records')

    # Демонстрация работы функциональностей
    print("\n" + "="*50)
    print("1. Главная страница:")
    main_page_data = main_page("2021-12-12 12:12:12", df)
    print(f"Приветствие: {main_page_data.get('greeting', 'Неизвестно')}")
    print(f"Количество карт: {len(main_page_data.get('cards', []))}")

    for card in main_page_data.get('cards', []):
        card_info = (
            f"  Карта {card['last_digits']}: потрачено "
            f"{card['total_spent']} руб., кешбэк {card['cashback']} руб."
        )
        print(card_info)

    top_count = len(main_page_data.get('top_transactions', []))
    print(f"Топ транзакций: {top_count}")

    for i, transaction in enumerate(main_page_data.get('top_transactions', [])[:3]):
        trans_info = (
            f"  {i+1}. {transaction['date']} - {transaction['amount']} "
            f"руб. - {transaction['category']}"
        )
        print(trans_info)

    print("\n" + "="*50)
    print("2. Простой поиск:")
    search_results = simple_search("Супермаркеты", transactions)
    print(f"Найдено транзакций по запросу 'Супермаркеты': {len(search_results)}")

    for i, transaction in enumerate(search_results[:3]):
        trans_info = (
            f"  {i+1}. {transaction['Категория']} - "
            f"{transaction['Описание']} - {transaction['Сумма операции']} руб."
        )
        print(trans_info)

    search_results2 = simple_search("магазин", transactions)
    print(f"Найдено транзакций по запросу 'магазин': {len(search_results2)}")

    print("\n" + "="*50)
    print("3. Траты по категории:")
    category_spending = spending_by_category(df, "Продукты", "2021-12-31")
    spent = category_spending.get('total_spent', 0)
    count = category_spending.get('transaction_count', 0)
    period = category_spending.get('period', {})

    print(f"Траты на 'Продукты': {spent} руб.")
    print(f"Количество транзакций: {count}")
    print(f"Период: {period.get('start', '')} - {period.get('end', '')}")

    print("\n" + "="*50)
    print("Анализ завершен!")


if __name__ == "__main__":
    main()
