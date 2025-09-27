"""
Тесты для функций сервисов из модуля services.
"""

from src.services import simple_search
from unittest.mock import patch


def test_simple_search():
    """
    Тестирование функции простого поиска.
    """
    # Подготовка тестовых данных
    test_transactions = [
        {"description": "Покупка в магазине", "category": "Продукты", "amount": 100},
        {"description": "Оплата услуг", "category": "Коммунальные услуги", "amount": 200},
        {"description": "Покупка в Apple Store", "category": "Развлечения", "amount": 300}
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


def test_simple_search_empty_query():
    """
    Тестирование поиска с пустым запросом.
    """
    test_transactions = [
        {"description": "Покупка в магазине", "category": "Продукты", "amount": 100}
    ]

    result = simple_search("", test_transactions)
    assert len(result) == 0

    result = simple_search("   ", test_transactions)
    assert len(result) == 0


def test_simple_search_empty_transactions():
    """
    Тестирование поиска с пустым списком транзакций.
    """
    result = simple_search("запрос", [])
    assert len(result) == 0


def test_simple_search_none_transactions():
    """
    Тестирование поиска с None вместо списка транзакций.
    """
    result = simple_search("запрос", None)
    assert result == []


def test_simple_search_special_characters():
    """
    Тестирование поиска со специальными символами.
    """
    test_transactions = [
        {"description": "Покупка в магазине", "category": "Продукты", "amount": 100},
        {"description": "Кафе-ресторан", "category": "Развлечения", "amount": 200}
    ]

    result = simple_search("кафе", test_transactions)
    assert len(result) == 1
    assert result[0]["description"] == "Кафе-ресторан"


def test_simple_search_case_insensitive():
    """
    Тестирование поиска без учета регистра.
    """
    test_transactions = [
        {"description": "Покупка в магазине", "category": "Продукты", "amount": 100},
        {"description": "Оплата услуг", "category": "Коммунальные услуги", "amount": 200}
    ]

    # Поиск в верхнем регистре
    result = simple_search("МАГАЗИН", test_transactions)
    assert len(result) == 1

    # Поиск в нижнем регистре
    result = simple_search("оплата", test_transactions)
    assert len(result) == 1


def test_simple_search_partial_match():
    """
    Тестирование частичного совпадения.
    """
    test_transactions = [
        {"description": "Супермаркет Лента", "category": "Продукты", "amount": 100},
        {"description": "Магазин электроники", "category": "Техника", "amount": 200}
    ]

    result = simple_search("маркет", test_transactions)
    assert len(result) == 1
    assert result[0]["description"] == "Супермаркет Лента"


def test_simple_search_multiple_matches():
    """
    Тестирование множественных совпадений.
    """
    test_transactions = [
        {"description": "Покупка в магазине", "category": "Продукты", "amount": 100},
        {"description": "Онлайн магазин", "category": "Интернет", "amount": 200},
        {"description": "Ресторан", "category": "Развлечения", "amount": 300}
    ]

    result = simple_search("магазин", test_transactions)
    assert len(result) == 2


def test_simple_search_transaction_with_missing_fields():
    """
    Тестирование поиска с транзакциями, в которых отсутствуют некоторые поля.
    """
    test_transactions = [
        {"description": "Нормальная транзакция", "category": "Продукты", "amount": 100},
        {"category": "Транзакция без описания", "amount": 200},  # Нет description
        {"description": "Транзакция без категории", "amount": 300},  # Нет category
        {"amount": 400}  # Только amount
    ]

    # Поиск должен работать с транзакциями, имеющими нужные поля
    result = simple_search("продукты", test_transactions)
    # Найдет только первую транзакцию, так как у нее есть категория "Продукты"
    assert len(result) == 1
    assert result[0]["description"] == "Нормальная транзакция"

    # Поиск по слову "транзакция" - найдет те, где есть это слово в description или category
    result = simple_search("транзакция", test_transactions)
    # Найдет первую (есть в description), вторую (есть в category) и третью (есть в description)
    assert len(result) == 3


def test_simple_search_only_description_field():
    """
    Тестирование поиска когда есть только поле description.
    """
    test_transactions = [
        {"description": "Транзакция с описанием", "amount": 100},  # Нет category
        {"amount": 200}  # Нет ни description, ни category
    ]

    result = simple_search("описанием", test_transactions)
    # Найдет только первую транзакцию
    assert len(result) == 1
    assert result[0]["description"] == "Транзакция с описанием"


def test_simple_search_only_category_field():
    """
    Тестирование поиска когда есть только поле category.
    """
    test_transactions = [
        {"category": "Транзакция с категорией", "amount": 100},  # Нет description
        {"amount": 200}  # Нет ни description, ни category
    ]

    result = simple_search("категорией", test_transactions)
    # Найдет только первую транзакцию
    assert len(result) == 1
    assert result[0]["category"] == "Транзакция с категорией"


@patch('src.services.logger')
def test_simple_search_logging(mock_logger):
    """
    Тестирование логирования в функции поиска.
    """
    test_transactions = [
        {"description": "Покупка в магазине", "category": "Продукты", "amount": 100}
    ]

    # Успешный поиск
    result = simple_search("магазин", test_transactions)
    assert len(result) == 1

    # Проверяем, что был вызван logger.info при успешном поиске
    info_calls = [call for call in mock_logger.info.call_args_list
                 if "Найдено" in str(call)]
    assert len(info_calls) > 0

    # Поиск с пустым запросом
    result = simple_search("", test_transactions)
    assert len(result) == 0

    # Проверяем, что был вызван logger.warning для пустого запроса
    warning_calls = [call for call in mock_logger.warning.call_args_list
                    if "пустой запрос" in str(call)]
    assert len(warning_calls) > 0


def test_simple_search_exact_match():
    """
    Тестирование точного совпадения.
    """
    test_transactions = [
        {"description": "Магазин", "category": "Розница", "amount": 100},
        {"description": "Супермаркет", "category": "Магазин продуктов", "amount": 200}
    ]

    # Точное совпадение с "Магазин"
    result = simple_search("Магазин", test_transactions)
    # Найдет первую (description "Магазин") и вторую (category "Магазин продуктов")
    assert len(result) == 2
