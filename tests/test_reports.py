import pandas as pd
from src.reports import spending_by_category
from unittest.mock import patch


def test_spending_by_category():
    """
    Тестирование функции расчета трат по категории.
    """
    test_data = {
        'Дата операции': ['2023-01-01', '2023-01-15', '2023-02-01', '2023-02-15', '2023-03-01'],
        'Категория': ['Продукты', 'Продукты', 'Развлечения', 'Продукты', 'Транспорт'],
        'Сумма операции': [100, 200, 300, 400, 500]
    }
    df = pd.DataFrame(test_data)

    # Вызов функции
    result = spending_by_category(df, "Продукты", "2023-03-15")

    # Проверка результатов
    assert result["category"] == "Продукты"
    assert result["total_spent"] == 700  # 100 + 200 + 400
    assert result["transaction_count"] == 3


@patch('src.reports.logger')
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


def test_spending_by_category_no_data():
    """
    Тестирование функции расчета трат по категории, когда данных нет.
    """
    test_data = {
        'Дата операции': ['2023-01-01', '2023-01-15'],
        'Категория': ['Транспорт', 'Развлечения'],
        'Сумма операции': [100, 200]
    }
    df = pd.DataFrame(test_data)

    result = spending_by_category(df, "Продукты", "2023-01-31")

    if result:
        assert "category" in result
        assert result["category"] == "Продукты"
        assert result["total_spent"] == 0
        assert result["transaction_count"] == 0
        assert "period" in result
    else:
        assert result == {}


def test_spending_by_category_missing_columns():
    """
    Тестирование функции расчета трат по категории при отсутствии колонок.
    """
    test_data = {
        'date': ['2023-01-01', '2023-01-15'],
        'amount': [100, 200]
    }
    df = pd.DataFrame(test_data)

    result = spending_by_category(df, "Продукты")

    assert result == {}
