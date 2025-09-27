import datetime
import json
import logging
from typing import Any, Dict, List

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def filter_transactions_by_date(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Фильтрует транзакции по дате.

    Args:
        df: DataFrame с транзакциями
        start_date: начальная дата в формате YYYY-MM-DD
        end_date: конечная дата в формате YYYY-MM-DD

    Returns:
        Отфильтрованный DataFrame
    """
    try:
        # Преобразование дат
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # Фильтрация
        mask = (pd.to_datetime(df["date"]) >= start) & (pd.to_datetime(df["date"]) <= end)
        return df.loc[mask]
    except Exception as e:
        logger.error(f"Ошибка при фильтрации транзакций по дате: {e}")
        return pd.DataFrame()


def calculate_card_stats(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Рассчитывает статистику по картам.

    Args:
        df: DataFrame с транзакциями

    Returns:
        Список со статистикой по картам
    """
    try:
        # Группировка по последним 4 цифрам карты
        card_stats = []

        # Проверяем, есть ли колонка 'card_number' в данных
        if "card_number" in df.columns:
            for card in df["card_number"].unique():
                card_df = df[df["card_number"] == card]
                # Суммируем только положительные amounts (траты)
                total_spent = card_df[card_df["amount"] > 0]["amount"].sum()
                cashback = total_spent * 0.01  # 1% кешбэк

                card_stats.append(
                    {
                        "last_digits": str(card)[-4:],
                        "total_spent": round(total_spent, 2),
                        "cashback": round(cashback, 2),
                    }
                )
        else:
            card_stats.append({"last_digits": "0000", "total_spent": 0, "cashback": 0})

        return card_stats
    except Exception as e:
        logger.error(f"Ошибка при расчете статистики по картам: {e}")
        return []


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает пользовательские настройки из JSON-файла.

    Returns:
        Словарь с настройками пользователя
    """
    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка при загрузке пользовательских настроек: {e}")
        return {"user_currencies": [], "user_stocks": []}
