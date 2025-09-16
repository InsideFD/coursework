import datetime
import json
import logging
from typing import Any, Dict, List

import pandas as pd

from src.utils import calculate_card_stats  # Добавляем импорт

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_greeting(time_str: str) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Args:
        time_str: строка с датой и временем в формате YYYY-MM-DD HH:MM:SS

    Returns:
        Строка с приветствием
    """
    try:
        time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        hour = time.hour

        if 5 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 17:
            return "Добрый день"
        elif 17 <= hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except Exception as e:
        logger.error(f"Ошибка при определении приветствия: {e}")
        return "Добрый день"


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """
    Получает курсы валют из внешнего API.

    Args:
        currencies: список валют для получения курсов

    Returns:
        Список словарей с курсами валют
    """
    try:
        results = []

        for currency in currencies:
            # Заглушка для демонстрации
            # В реальности здесь будет запрос к API
            if currency == "USD":
                results.append({"currency": currency, "rate": 73.21})
            elif currency == "EUR":
                results.append({"currency": currency, "rate": 87.08})

        return results
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return []


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает цены акций из внешнего API.

    Args:
        stocks: список акций для получения цен

    Returns:
        Список словарей с ценами акций
    """
    try:
        results = []

        for stock in stocks:
            # Заглушка для демонстрации
            # В реальности здесь будет запрос к API
            if stock == "AAPL":
                results.append({"stock": stock, "price": 150.12})
            elif stock == "AMZN":
                results.append({"stock": stock, "price": 3173.18})

        return results
    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {e}")
        return []


def main_page(date_time: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Генерирует JSON-ответ для главной страницы.

    Args:
        date_time: строка с датой и временем в формате YYYY-MM-DD HH:MM:SS
        df: DataFrame с транзакциями

    Returns:
        Словарь с данными для главной страницы
    """
    try:
        # Загрузка пользовательских настроек
        with open("user_settings.json", "r") as f:
            settings = json.load(f)

        # Получение статистики по картам
        cards_stats = calculate_card_stats(df)

        # Формирование ответа
        response = {
            "greeting": get_greeting(date_time),
            "cards": cards_stats,  # Используем реальную функцию
            "top_transactions": [],
            "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
            "stock_prices": get_stock_prices(settings.get("user_stocks", [])),
        }

        return response
    except Exception as e:
        logger.error(f"Ошибка при формировании главной страницы: {e}")
        return {}
