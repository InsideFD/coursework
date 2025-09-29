"""
Тесты для функций сервисов из модуля services.
"""

from src.services import simple_search
from unittest.mock import patch


def test_simple_search():
    """
    Тестирование функции простого поиска.
    """
    test_transactions = [
        {"Описание": "Покупка в магазине", "Категория": "Продукты", "Сумма операции": 100},
        {"Описание": "Оплата услуг", "Категория": "Коммунальные услуги", "Сумма операции": 200},
        {"Описание": "Покупка в Apple Store", "Категория": "Развлечения", "Сумма операции": 300}
    ]

    # Тестирование поиска по описанию
    result = simple_search("магазин", test_transactions)
    assert len(result) == 1
    assert result[0]["Описание"] == "Покупка в магазине"

    # Тестирование поиска по категории
    result = simple_search("развлечения", test_transactions)
    assert len(result) == 1
    assert result[0]["Категория"] == "Развлечения"

    # Тестирование поиска без результатов
    result = simple_search("несуществующий запрос", test_transactions)
    assert len(result) == 0


def test_simple_search_empty_query():
    """
    Тестирование поиска с пустым запросом.
    """
    test_transactions = [
        {"Описание": "Покупка в магазине", "Категория": "Продукты", "Сумма операции": 100}
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
        {"Описание": "Покупка в магазине", "Категория": "Продукты", "Сумма операции": 100},
        {"Описание": "Кафе-ресторан", "Категория": "Развлечения", "Сумма операции": 200}
    ]

    result = simple_search("кафе", test_transactions)
    assert len(result) == 1
    assert result[0]["Описание"] == "Кафе-ресторан"


def test_simple_search_case_insensitive():
    """
    Тестирование поиска без учета регистра.
    """
    test_transactions = [
        {"Описание": "Покупка в магазине", "Категория": "Продукты", "Сумма операции": 100},
        {"Описание": "Оплата услуг", "Категория": "Коммунальные услуги", "Сумма операции": 200}
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
        {"Описание": "Супермаркет Лента", "Категория": "Продукты", "Сумма операции": 100},
        {"Описание": "Магазин электроники", "Категория": "Техника", "Сумма операции": 200},
        {"Описание": "Аптека", "Категория": "Медицина", "Сумма операции": 50}
    ]

    result = simple_search("маркет", test_transactions)
    assert len(result) == 1
    assert result[0]["Описание"] == "Супермаркет Лента"


def test_simple_search_multiple_matches():
    """
    Тестирование множественных совпадений.
    """
    test_transactions = [
        {"Описание": "Супермаркет Лента", "Категория": "Продукты", "Сумма операции": 100},
        {"Описание": "Супермаркет Ашан", "Категория": "Продукты", "Сумма операции": 150},
        {"Описание": "Кофе", "Категория": "Кафе", "Сумма операции": 50}
    ]

    result = simple_search("супермаркет", test_transactions)
    assert len(result) == 2


def test_simple_search_transaction_with_missing_fields():
    """
    Тестирование поиска с транзакциями, в которых отсутствуют некоторые поля.
    """
    test_transactions = [
        {"Описание": "Покупка в магазине", "Категория": "Продукты", "Сумма операции": 100},
        {"Описание": "", "Категория": "Транспорт", "Сумма операции": 200},
        {"Категория": "Развлечения", "Сумма операции": 300},
        {"Описание": "Такси", "Сумма операции": 400}
    ]

    result = simple_search("продукты", test_transactions)
    assert len(result) == 1


def test_simple_search_only_description_field():
    """
    Тестирование поиска только по полю описания.
    """
    test_transactions = [
        {"Описание": "Покупка в магазине", "Сумма операции": 100},
        {"Категория": "Магазин", "Сумма операции": 200}
    ]

    result = simple_search("магазин", test_transactions)
    assert len(result) == 2


def test_simple_search_only_category_field():
    """
    Тестирование поиска только по полю категории.
    """
    test_transactions = [
        {"Описание": "Покупка", "Сумма операции": 100},
        {"Категория": "Магазин", "Сумма операции": 200}
    ]

    result = simple_search("магазин", test_transactions)
    assert len(result) == 1
    assert result[0]["Категория"] == "Магазин"


@patch('src.services.logger')
def test_simple_search_logging(mock_logger):
    """
    Тестирование логирования при поиске.
    """
    test_transactions = [
        {"Описание": "Покупка в магазине", "Категория": "Продукты", "Сумма операции": 100}
    ]

    result = simple_search("магазин", test_transactions)
    assert len(result) == 1
    assert mock_logger.info.called


def test_simple_search_exact_match():
    """
    Тестирование точного совпадения.
    """
    test_transactions = [
        {"Описание": "Магазин", "Категория": "Продукты", "Сумма операции": 100},
        {"Описание": "Интернет-магазин", "Категория": "Онлайн покупки", "Сумма операции": 200},
        {"Описание": "Магазин электроники", "Категория": "Техника", "Сумма операции": 300}
    ]

    result = simple_search("магазин", test_transactions)
    assert len(result) == 3


@patch('src.services.logger')
def test_simple_search_transaction_error(mock_logger):
    """
    Тестирование обработки ошибок в отдельных транзакциях.
    """
    class ProblemObject:
        def __str__(self):
            raise Exception("Тестовая ошибка при преобразовании в строку")

    problem_transactions = [
        {"Описание": "Нормальная транзакция", "Категория": "Продукты", "Сумма операции": 100},
        {"Описание": ProblemObject(), "Категория": ProblemObject()}  # Объекты, которые вызовут исключение
    ]

    result = simple_search("продукты", problem_transactions)

    assert len(result) == 1
    assert result[0]["Описание"] == "Нормальная транзакция"


def test_simple_search_with_invalid_transaction_structure():
    """
    Тестирование поиска с транзакциями, имеющими неверную структуру.
    """
    test_transactions = [
        {"Описание": "Нормальная транзакция", "Категория": "Продукты", "Сумма операции": 100},
        {"invalid_field": "value"}  # Транзакция без нужных полей
    ]

    result = simple_search("продукты", test_transactions)

    assert len(result) == 1
    assert result[0]["Описание"] == "Нормальная транзакция"
