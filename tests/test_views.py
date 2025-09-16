from unittest.mock import patch
import pandas as pd
from src.views import get_greeting, main_page


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


@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("src.views.calculate_card_stats")  # Мокаем функцию в views
def test_main_page(mock_calculate_card_stats, mock_get_stock_prices, mock_get_currency_rates):
    """
    Тестирование функции главной страницы.
    """
    # Настройка моков
    mock_calculate_card_stats.return_value = [{"last_digits": "1234", "total_spent": 100, "cashback": 1}]
    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 75.5}]
    mock_get_stock_prices.return_value = [{"stock": "AAPL", "price": 150.0}]

    # Создание тестовых данных
    test_data = {
        "date": ["2023-01-01", "2023-01-02"],
        "amount": [100, 200],
        "card_number": ["1234567812345678", "1234567812345678"],
    }
    df = pd.DataFrame(test_data)

    # Вызов функции
    result = main_page("2023-01-01 12:00:00", df)

    # Проверка результатов
    assert result["greeting"] == "Добрый день"
    assert len(result["cards"]) == 1
    assert result["cards"][0]["last_digits"] == "1234"
    assert len(result["currency_rates"]) == 1
    assert len(result["stock_prices"]) == 1

    mock_calculate_card_stats.assert_called_once_with(df)
    mock_get_currency_rates.assert_called_once()
    mock_get_stock_prices.assert_called_once()
