"""
Тесты для функций сервисов из модуля services.
"""

from unittest.mock import patch

from src.services import simple_search


def test_simple_search():
    """
    Тестирование функции простого поиска.
    """
    # Подготовка тестовых данных
    test_transactions = [
        {"description": "Покупка в магазине", "category": "Продукты", "amount": 100},
        {"description": "Оплата услуг", "category": "Коммунальные услуги", "amount": 200},
        {"description": "Покупка в Apple Store", "category": "Развлечения", "amount": 300},
    ]

    # Тестирование поиска по описанию
    result = simple_search("магазин", test_transactions)
    assert len(result) == 1
    assert result[0]["description"] == "Покупка в магазине"

    # Тестирование поиска по категории
    result = simple_search("развлечения", test_transactions)
    assert len(result) == 1
    assert result[0]["category"] == "Развлечения"

    # Тестирование поиска без результатов
    result = simple_search("несуществующий запрос", test_transactions)
    assert len(result) == 0


@patch("src.services.logger")
def test_simple_search_error(mock_logger):
    """
    Тестирование обработки ошибок в функции простого поиска.
    """
    # Тестирование с некорректными данными
    result = simple_search("запрос", None)
    assert result == []
    mock_logger.error.assert_called_once()
