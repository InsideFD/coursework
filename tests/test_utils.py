from unittest.mock import mock_open, patch

import pandas as pd

from src.utils import calculate_card_stats, filter_transactions_by_date, load_user_settings


def test_filter_transactions_by_date():
    """
    Тестирование фильтрации транзакций по дате.
    """
    # Создание тестовых данных
    test_data = {"date": ["2023-01-01", "2023-01-15", "2023-02-01"], "amount": [100, 200, 300]}
    df = pd.DataFrame(test_data)

    # Фильтрация
    result = filter_transactions_by_date(df, "2023-01-01", "2023-01-31")

    # Проверка результатов
    assert len(result) == 2
    assert all(result["date"].isin(["2023-01-01", "2023-01-15"]))


def test_calculate_card_stats():
    """
    Тестирование расчета статистики по картам.
    """
    # Создание тестовых данных
    test_data = {
        "card_number": ["1234567812345678", "1234567812345678", "8765432187654321"],
        "amount": [100, 200, -50],  # Отрицательная сумма - пополнение
    }
    df = pd.DataFrame(test_data)

    # Расчет статистики
    result = calculate_card_stats(df)

    # Проверка результатов
    assert len(result) == 2
    assert any(stats["last_digits"] == "5678" for stats in result)
    assert any(stats["last_digits"] == "4321" for stats in result)


def test_calculate_card_stats_no_card_column():
    """
    Тестирование расчета статистики по картам, когда колонка card_number отсутствует.
    """
    # Создание тестовых данных без колонки card_number
    test_data = {"date": ["2023-01-01", "2023-01-02"], "amount": [100, 200]}
    df = pd.DataFrame(test_data)

    # Расчет статистики
    result = calculate_card_stats(df)

    # Проверка результатов - должна быть заглушка
    assert len(result) == 1
    assert result[0]["last_digits"] == "0000"
    assert result[0]["total_spent"] == 0


@patch("builtins.open", mock_open(read_data='{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}'))
def test_load_user_settings():
    """
    Тестирование загрузки пользовательских настроек.
    """
    result = load_user_settings()

    # Проверка результатов
    assert result["user_currencies"] == ["USD", "EUR"]
    assert result["user_stocks"] == ["AAPL"]


@patch("builtins.open", side_effect=FileNotFoundError)
def test_load_user_settings_file_not_found(mock_open):
    """
    Тестирование загрузки пользовательских настроек, когда файл не найден.
    """
    result = load_user_settings()

    # Проверка результатов - должны быть пустые списки
    assert result["user_currencies"] == []
    assert result["user_stocks"] == []
