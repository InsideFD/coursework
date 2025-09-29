import pandas as pd
import datetime
import logging
from typing import Optional, Dict, Any
from functools import wraps

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def report_decorator(filename=None):
    """
    Декоратор для записи реальных результатов отчета в файл.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if filename is None:
                report_filename = (
                    f"report_{func.__name__}_"
                    f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
            else:
                report_filename = filename

            try:
                import json
                with open(report_filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"Реальный отчет сохранен в файл: {report_filename}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении реального отчета: {e}")

            return result

        return wrapper

    return decorator


def filter_data_by_period(df: pd.DataFrame, date: Optional[str] = None,
                          months: int = 3) -> pd.DataFrame:
    """
    Фильтрует реальные данные за указанный период.
    """
    try:
        if date is None:
            end_date = datetime.datetime.now()
        else:
            end_date = datetime.datetime.strptime(date, "%Y-%m-%d")

        # Расчет даты начала периода (реальные 3 месяца)
        if months == 3:
            if end_date.month > 3:
                start_date = end_date.replace(month=end_date.month - 3, day=1)
            else:
                new_year = end_date.year - 1
                new_month = 12 - end_date.month + 3
                start_date = end_date.replace(year=new_year, month=new_month, day=1)
        else:
            start_date = end_date.replace(day=1) - datetime.timedelta(days=1)
            start_date = start_date.replace(day=1)

        df_copy = df.copy()
        df_copy['Дата операции'] = pd.to_datetime(df_copy['Дата операции'], errors='coerce')
        df_copy = df_copy.dropna(subset=['Дата операции'])

        filtered_df = df_copy[
            (df_copy['Дата операции'] >= start_date) &
            (df_copy['Дата операции'] <= end_date)
            ]

        logger.info(
            f"Отфильтровано {len(filtered_df)} реальных транзакций за период "
            f"с {start_date.date()} по {end_date.date()}"
        )
        return filtered_df
    except Exception as e:
        logger.error(f"Ошибка при фильтрации реальных данных по периоду: {e}")
        return df


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str,
                         date: Optional[str] = None) -> Dict[str, Any]:
    """
    Рассчитывает реальные траты по категории за последние три месяца.
    """
    try:
        if 'Категория' not in transactions.columns or 'Сумма операции' not in transactions.columns:
            logger.error("В реальных данных отсутствуют необходимые колонки")
            return {}

        # Фильтрация реальных данных за период
        filtered_df = filter_data_by_period(transactions, date, months=3)

        if filtered_df.empty:
            logger.warning("Нет реальных данных за указанный период")
            return {
                "category": category,
                "period": {"start": "", "end": ""},
                "total_spent": 0,
                "transaction_count": 0
            }

        category_df = filtered_df[filtered_df['Категория'] == category]

        if category_df.empty:
            logger.info(f"Нет реальных транзакций в категории '{category}'")
            if date is None:
                end_date = datetime.datetime.now()
            else:
                end_date = datetime.datetime.strptime(date, "%Y-%m-%d")

            if end_date.month > 3:
                start_date = end_date.replace(month=end_date.month - 3, day=1)
            else:
                new_year = end_date.year - 1
                new_month = 12 - end_date.month + 3
                start_date = end_date.replace(year=new_year, month=new_month, day=1)

            return {
                "category": category,
                "period": {
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                },
                "total_spent": 0,
                "transaction_count": 0
            }

        total_spent = category_df['Сумма операции'].sum()

        # Определение реальных дат периода
        if date is None:
            end_date = datetime.datetime.now()
        else:
            end_date = datetime.datetime.strptime(date, "%Y-%m-%d")

        if end_date.month > 3:
            start_date = end_date.replace(month=end_date.month - 3, day=1)
        else:
            new_year = end_date.year - 1
            new_month = 12 - end_date.month + 3
            start_date = end_date.replace(year=new_year, month=new_month, day=1)

        # Формирование реального результата
        result = {
            "category": category,
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "total_spent": round(total_spent, 2),
            "transaction_count": len(category_df)
        }

        logger.info(
            f"Рассчитаны реальные траты по категории '{category}': "
            f"{total_spent} руб., {len(category_df)} транзакций"
        )
        return result
    except Exception as e:
        logger.error(f"Ошибка при расчете реальных трат по категории: {e}")
        return {}
