import pandas as pd
from src.utils import filter_transactions_by_date, calculate_card_stats, load_user_settings
from unittest.mock import mock_open, patch


def test_filter_transactions_by_date():
    """
    Тестирование фильтрации транзакций по дате.
    """
    test_data = {
        'Дата операции': ['2023-01-01', '2023-01-15', '2023-02-01'],
        'Сумма операции': [100, 200, 300]
    }
    df = pd.DataFrame(test_data)

    # Фильтрация
    result = filter_transactions_by_date(df, '2023-01-01', '2023-01-31')

    assert len(result) == 2
    assert all(result['Дата операции'].isin(['2023-01-01', '2023-01-15']))


def test_calculate_card_stats():
    """
    Тестирование расчета статистики по картам.
    """

    test_data = {
        'Номер карты': ['1234567812345678', '1234567812345678', '8765432187654321'],
        'Сумма операции': [100, 200, -50]  # Отрицательная сумма - пополнение
    }
    df = pd.DataFrame(test_data)

    result = calculate_card_stats(df)

    assert len(result) == 2
    assert any(stats['last_digits'] == '5678' for stats in result)
    assert any(stats['last_digits'] == '4321' for stats in result)


def test_calculate_card_stats_no_card_column():
    """
    Тестирование расчета статистики по картам, когда колонка card_number отсутствует.
    """
    test_data = {
        'Дата операции': ['2023-01-01', '2023-01-02'],
        'Сумма операции': [100, 200]
    }
    df = pd.DataFrame(test_data)

    result = calculate_card_stats(df)

    assert len(result) == 1
    assert result[0]["last_digits"] == "0000"
    total_spent = df[df['Сумма операции'] > 0]['Сумма операции'].sum()
    assert result[0]["total_spent"] == total_spent


@patch('builtins.open', mock_open(read_data='{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}'))
def test_load_user_settings():
    """
    Тестирование загрузки пользовательских настроек.
    """
    result = load_user_settings()

    assert result["user_currencies"] == ["USD", "EUR"]
    assert result["user_stocks"] == ["AAPL"]


@patch('builtins.open', side_effect=FileNotFoundError)
def test_load_user_settings_file_not_found(mock_open):
    """
    Тестирование загрузки пользовательских настроек, когда файл не найден.
    """
    result = load_user_settings()

    assert result["user_currencies"] == []
    assert result["user_stocks"] == []
