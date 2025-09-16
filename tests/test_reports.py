"""
Тесты для функций отчетов из модуля reports.
"""

from unittest.mock import patch

import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category():
    """
    Тестирование функции расчета трат по категории.
    """
    # Создание тестовых данных
    test_data = {
        "date": ["2023-01-01", "2023-01-15", "2023-02-01", "2023-03-01"],
        "category": ["Продукты", "Продукты", "Развлечения", "Продукты"],
        "amount": [100, 200, 300, 400],
    }
    df = pd.DataFrame(test_data)

    # Вызов функции
    result = spending_by_category(df, "Продукты", "2023-03-15")

    # Проверка результатов
    assert result["category"] == "Продукты"
    assert result["total_spent"] == 700  # 100 + 200 + 400
    assert result["transaction_count"] == 3


@patch("src.reports.logger")
def test_spending_by_category_error(mock_logger):
    """
    Тестирование обработки ошибок в функции расчета трат по категории.
    """
    # Вызов с некорректными данными
    result = spending_by_category(pd.DataFrame(), "Продукты", "некорректная дата")

    # Проверка, что функция вернула пустой результат
    assert result == {}

    # Проверка, что ошибка была залогирована
    mock_logger.error.assert_called_once()
