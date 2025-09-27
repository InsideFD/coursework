"""
Тесты для функций представлений из модуля views.
"""

import pandas as pd
from src.views import main_page, get_greeting, get_currency_rates, get_stock_prices
from unittest.mock import patch, MagicMock


def test_get_greeting():
    """
    Тестирование функции определения приветствия.
    """
    # Утро (5-11 часов)
    assert get_greeting("2023-01-01 08:00:00") == "Доброе утро"

    # День (12-16 часов)
    assert get_greeting("2023-01-01 14:00:00") == "Добрый день"

    # Вечер (17-22 часа)
    assert get_greeting("2023-01-01 20:00:00") == "Добрый вечер"

    # Ночь (23-4 часа)
    assert get_greeting("2023-01-01 02:00:00") == "Доброй ночи"


@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
@patch('src.views.calculate_card_stats')
@patch('src.views.get_top_transactions')
@patch('src.views.filter_data_by_month')
@patch('src.views.load_user_settings')
def test_main_page(mock_load_settings, mock_filter_data, mock_get_top_transactions,
                   mock_calculate_card_stats, mock_get_stock_prices, mock_get_currency_rates):
    """
    Тестирование функции главной страницы.
    """
    # Настройка моков
    mock_load_settings.return_value = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN"]
    }

    # Создаем тестовый DataFrame с правильной структурой
    test_data = {
        'date': ['2023-01-01', '2023-01-02'],
        'amount': [100, 200],
        'card_number': ['1234567812345678', '1234567812345678'],
        'category': ['Продукты', 'Транспорт'],
        'description': ['Магазин', 'Такси']
    }
    original_df = pd.DataFrame(test_data)

    # Мок для фильтрованного DataFrame (должен быть таким же)
    filtered_df = pd.DataFrame(test_data)
    mock_filter_data.return_value = filtered_df

    mock_calculate_card_stats.return_value = [
        {"last_digits": "1234", "total_spent": 100, "cashback": 1}
    ]
    mock_get_top_transactions.return_value = [
        {
            "date": "01.01.2023",
            "amount": 100.0,
            "category": "Продукты",
            "description": "Магазин"
        }
    ]
    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 75.5}]
    mock_get_stock_prices.return_value = [{"stock": "AAPL", "price": 150.0}]

    # Вызов функции
    result = main_page("2023-01-01 12:00:00", original_df)

    # Проверка результатов
    assert result["greeting"] == "Добрый день"
    assert len(result["cards"]) == 1
    assert result["cards"][0]["last_digits"] == "1234"
    assert len(result["currency_rates"]) == 1
    assert len(result["stock_prices"]) == 1

    # Проверка вызовов моков
    mock_load_settings.assert_called_once()
    mock_filter_data.assert_called_once_with(original_df, "2023-01-01 12:00:00")
    mock_calculate_card_stats.assert_called_once_with(filtered_df)
    mock_get_top_transactions.assert_called_once_with(filtered_df)
    mock_get_currency_rates.assert_called_once_with(["USD", "EUR"])
    mock_get_stock_prices.assert_called_once_with(["AAPL", "AMZN"])


@patch('src.views.requests.get')
@patch('src.views.os.getenv')
def test_get_currency_rates(mock_getenv, mock_get):
    """
    Тестирование получения курсов валют через API.
    """
    # Настройка моков
    mock_getenv.return_value = "test_api_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "rates": {
            "USD": 1.0,
            "EUR": 0.85,
            "RUB": 75.5
        }
    }
    mock_get.return_value = mock_response

    # Вызов функции
    result = get_currency_rates(["USD", "EUR"])

    # Проверка результатов
    assert len(result) == 2
    assert any(r["currency"] == "USD" for r in result)
    assert any(r["currency"] == "EUR" for r in result)


@patch('src.views.requests.get')
@patch('src.views.os.getenv')
def test_get_stock_prices(mock_getenv, mock_get):
    """
    Тестирование получения цен акций через API.
    """
    # Настройка моков
    mock_getenv.return_value = "test_api_key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "date": "2023-01-01",
            "close": 150.12,
            "high": 152.0,
            "low": 149.5,
            "open": 150.0,
            "volume": 1000000
        }
    ]
    mock_get.return_value = mock_response

    # Вызов функции
    result = get_stock_prices(["AAPL"])

    # Проверка результатов
    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.12


@patch('src.views.logger')
def test_main_page_error_handling(mock_logger):
    """
    Тестирование обработки ошибок в функции главной страницы.
    """
    # Создаем DataFrame с некорректными данными
    test_data = {
        'date': ['invalid_date', 'another_invalid'],
        'amount': [100, 200]
    }
    df = pd.DataFrame(test_data)

    # Вызов функции с некорректными данными
    result = main_page("invalid_date", df)

    # Проверка, что функция возвращает корректную структуру даже при ошибках
    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result

    # Проверка, что ошибка была залогирована
    assert mock_logger.error.called


def test_main_page_empty_dataframe():
    """
    Тестирование функции главной страницы с пустым DataFrame.
    """
    # Создаем пустой DataFrame
    empty_df = pd.DataFrame()

    # Вызов функции с пустыми данными
    result = main_page("2023-01-01 12:00:00", empty_df)

    # Проверка, что функция возвращает корректную структуру
    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result
