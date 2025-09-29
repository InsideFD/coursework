import pandas as pd
import datetime
import logging
import json
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def filter_transactions_by_date(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Фильтрует транзакции по дате.
    """
    try:
        # Преобразование дат
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        mask = (pd.to_datetime(df['Дата операции']) >= start) & (pd.to_datetime(df['Дата операции']) <= end)
        return df.loc[mask]
    except Exception as e:
        logger.error(f"Ошибка при фильтрации транзакций по дате: {e}")
        return pd.DataFrame()


def calculate_card_stats(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Рассчитывает статистику по картам.
    """
    try:
        card_stats = []

        # Проверяем наличие колонки с правильным названием
        if 'Номер карты' in df.columns:
            for card in df['Номер карты'].unique():
                if pd.isna(card):  # Пропускаем NaN значения
                    continue
                card_df = df[df['Номер карты'] == card]
                # Суммируем только положительные amounts (траты)
                total_spent = card_df[card_df['Сумма операции'] > 0]['Сумма операции'].sum()
                cashback = total_spent * 0.01

                card_stats.append({
                    "last_digits": str(card)[-4:],
                    "total_spent": round(total_spent, 2),
                    "cashback": round(cashback, 2)
                })
        else:
            total_spent = df[df['Сумма операции'] > 0]['Сумма операции'].sum()
            if total_spent > 0:
                card_stats.append({
                    "last_digits": "0000",
                    "total_spent": round(total_spent, 2),
                    "cashback": round(total_spent * 0.01, 2)
                })

        return card_stats
    except Exception as e:
        logger.error(f"Ошибка при расчете статистики по картам: {e}")
        return []


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает пользовательские настройки из JSON-файла.
    """
    try:
        with open('user_settings.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка при загрузке пользовательских настроек: {e}")
        return {"user_currencies": [], "user_stocks": []}
