import datetime
import json
import logging
from functools import wraps
from typing import Any, Dict, Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def report_decorator(filename=None):
    """
    Декоратор для записи результатов отчета в файл.

    Args:
        filename: имя файла для сохранения результатов

    Returns:
        Декорированная функция
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Определение имени файла
            if filename is None:
                report_filename = f"report_{func.__name__}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                report_filename = filename

            # Запись в файл
            try:
                with open(report_filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"Отчет сохранен в файл: {report_filename}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета: {e}")

            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Рассчитывает траты по категории за последние 3 месяца.

    Args:
        transactions: DataFrame с транзакциями
        category: категория для анализа
        date: дата отсчета (если None, используется текущая дата)

    Returns:
        Словарь с результатами анализа
    """
    try:
        # Определение даты отсчета
        if date is None:
            end_date = datetime.datetime.now()
        else:
            end_date = datetime.datetime.strptime(date, "%Y-%m-%d")

        # Расчет даты начала периода (3 месяца назад)
        start_date = end_date - datetime.timedelta(days=90)

        # Фильтрация транзакций по категории и дате
        filtered_df = transactions[
            (transactions["category"] == category)
            & (pd.to_datetime(transactions["date"]) >= start_date)
            & (pd.to_datetime(transactions["date"]) <= end_date)
        ]

        # Суммирование трат
        total_spent = filtered_df["amount"].sum()

        # Формирование результата
        result = {
            "category": category,
            "period": {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")},
            "total_spent": round(total_spent, 2),
            "transaction_count": len(filtered_df),
        }

        logger.info(f"Рассчитаны траты по категории '{category}': {total_spent} руб.")
        return result
    except Exception as e:
        logger.error(f"Ошибка при расчете трат по категории: {e}")
        return {}
