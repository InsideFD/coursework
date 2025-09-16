from datetime import datetime
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.reports import spending_by_category
from src.services import simple_search
from src.views import main_page


def load_transactions(file_path: str) -> pd.DataFrame:
    """
    Загружает транзакции из Excel-файла.

    Args:
        file_path: путь к Excel-файлу с транзакциями

    Returns:
        DataFrame с транзакциями
    """
    try:
        df = pd.read_excel(file_path)
        print(f"Успешно загружено {len(df)} транзакций")
        return df
    except Exception as e:
        print(f"Ошибка при загрузке транзакций: {e}")
        return pd.DataFrame()


def main():
    """
    Главная функция приложения.
    Запускает все реализованные функциональности.
    """
    print("Запуск анализатора транзакций...")

    # Загрузка транзакций
    df = load_transactions("data/operations.xlsx")
    if df.empty:
        print("Не удалось загрузить транзакции. Завершение работы.")
        return

    # Преобразование в список словарей для сервисов
    transactions = df.to_dict("records")

    # Демонстрация работы функциональностей
    print("\n1. Главная страница:")
    main_page_data = main_page(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), df)
    print(f"Приветствие: {main_page_data.get('greeting', 'Неизвестно')}")

    print("\n2. Простой поиск:")
    search_results = simple_search("магазин", transactions)
    print(f"Найдено транзакций: {len(search_results)}")

    print("\n3. Траты по категории:")
    category_spending = spending_by_category(df, "Продукты")
    print(f"Траты на продукты: {category_spending.get('total_spent', 0)} руб.")

    print("\nАнализ завершен!")


if __name__ == "__main__":
    main()
