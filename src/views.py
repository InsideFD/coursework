import os
import json
import pandas as pd
import datetime
import logging
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает пользовательские настройки из JSON-файла.
    """
    try:
        settings_path = os.path.join(
            os.path.dirname(__file__), '..', 'user_settings.json'
        )
        absolute_path = os.path.abspath(settings_path)

        print(f"Загрузка настроек из: {absolute_path}")

        with open(absolute_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            print(f"Загружены настройки: {settings}")
            return settings
    except Exception as e:
        logger.error(f"Ошибка при загрузке пользовательских настроек: {e}")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}


def get_greeting(time_str: str) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.
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
    Получает реальные курсы валют из API apilayer.com.
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            logger.error("API_KEY не найден в переменных окружения")
            return []

        # API endpoint для курсов валют
        url = "https://api.apilayer.com/exchangerates_data/latest?base=USD"

        headers = {"apikey": api_key}
        logger.info(f"Запрос реальных курсов валют для: {currencies}")

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})

            results = []
            for currency in currencies:
                if currency in rates:
                    rate = rates[currency]
                    results.append({
                        "currency": currency,
                        "rate": round(rate, 2)
                    })
                    logger.info(f"Реальный курс {currency}: {rate}")
                else:
                    logger.warning(f"Курс для валюты {currency} не найден в ответе API")

            print(f"Получены реальные курсы валют: {results}")
            return results
        else:
            logger.error(f"Ошибка API: {response.status_code} - {response.text}")
            return []

    except requests.exceptions.Timeout:
        logger.error("Таймаут при запросе к API курсов валют")
        return []
    except requests.exceptions.ConnectionError:
        logger.error("Ошибка соединения с API курсов валют")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении курсов валют: {e}")
        return []


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает реальные цены акций из API apilayer.com
    """
    try:
        api_key = os.getenv('API_KEY')
        if not api_key:
            logger.error("API_KEY не найден в переменных окружения")
            return []

        headers = {"apikey": api_key}
        results = []

        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

        for stock in stocks:
            try:
                url = (f"https://api.apilayer.com/tiingo/tiingo/daily/{stock}/prices"
                       f"?startDate={start_date}&endDate={end_date}")

                logger.info(f"Запрос реальной цены акции: {stock}")
                response = requests.get(url, headers=headers, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        latest_data = data[-1]
                        latest_price = latest_data.get('close', 0)
                        results.append({
                            "stock": stock,
                            "price": round(latest_price, 2)
                        })
                        logger.info(f"Реальная цена акции {stock}: {latest_price}")
                    else:
                        logger.warning(f"Данные по акции {stock} не найдены в API")
                else:
                    error_msg = f"Ошибка API для акции {stock}: {response.status_code}"
                    logger.error(error_msg)

            except requests.exceptions.Timeout:
                logger.error(f"Таймаут при запросе цены акции {stock}")
            except requests.exceptions.ConnectionError:
                logger.error(f"Ошибка соединения при запросе цены акции {stock}")
            except Exception as e:
                logger.error(f"Ошибка при получении цены акции {stock}: {e}")

        print(f"Получены реальные цены акций: {results}")
        return results

    except Exception as e:
        logger.error(f"Общая ошибка при получении цен акций: {e}")
        return []


def calculate_card_stats(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Рассчитывает статистику по картам на основе реальных данных.
    """
    try:
        card_stats = []

        # Проверяем наличие необходимых колонок
        if 'card_number' not in df.columns:
            logger.warning("Колонка 'card_number' не найдена в данных")
            total_spent = df[df['amount'] > 0]['amount'].sum()
            if total_spent > 0:
                card_stats.append({
                    "last_digits": "0000",
                    "total_spent": round(total_spent, 2),
                    "cashback": round(total_spent * 0.01, 2)
                })
            return card_stats

        valid_cards = [card for card in df['card_number'].unique() if not pd.isna(card)]

        for card in valid_cards:
            card_df = df[df['card_number'] == card]
            # Суммируем только положительные amounts (траты)
            total_spent = card_df[card_df['amount'] > 0]['amount'].sum()

            if total_spent > 0:
                cashback = total_spent * 0.01

                # Форматируем номер карты
                card_str = str(card).strip()
                last_digits = (card_str[-4:] if len(card_str) >= 4
                               else card_str.zfill(4)[-4:])

                card_stats.append({
                    "last_digits": last_digits,
                    "total_spent": round(total_spent, 2),
                    "cashback": round(cashback, 2)
                })

        # Если нет карт с тратами, создаем пустую статистику
        if not card_stats:
            logger.info("Нет данных о тратах по картам")

        print(f"Рассчитана реальная статистика по картам: {len(card_stats)} карт")
        return card_stats
    except Exception as e:
        logger.error(f"Ошибка при расчете статистики по картам: {e}")
        return []


def get_top_transactions(df: pd.DataFrame, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Возвращает реальные топ транзакций по сумме.
    """
    try:
        # Проверяем наличие необходимых колонок
        required_columns = ['date', 'amount', 'category', 'description']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.warning(f"Отсутствуют колонки: {missing_columns}")
            return []

        # Берем транзакции с положительной суммой (траты)
        expenses_df = df[df['amount'] > 0].copy()

        if expenses_df.empty:
            logger.info("Нет данных о тратах за период")
            return []

        # Сортируем по убыванию суммы и берем топ
        top_df = expenses_df.nlargest(limit, 'amount')

        # Форматируем результат
        top_transactions = []
        for _, row in top_df.iterrows():
            # Форматируем дату
            try:
                if hasattr(row['date'], 'strftime'):
                    formatted_date = row['date'].strftime("%d.%m.%Y")
                else:
                    date_obj = pd.to_datetime(row['date'])
                    formatted_date = date_obj.strftime("%d.%m.%Y")
            except Exception:
                formatted_date = str(row['date'])[:10]

            transaction = {
                "date": formatted_date,
                "amount": round(float(row['amount']), 2),
                "category": str(row.get('category', 'Неизвестно')),
                "description": str(row.get('description', ''))
            }
            top_transactions.append(transaction)

        print(f"Сформирован реальный топ транзакций: {len(top_transactions)}")
        return top_transactions
    except Exception as e:
        logger.error(f"Ошибка при формировании топ транзакций: {e}")
        return []


def filter_data_by_month(df: pd.DataFrame, date_time: str) -> pd.DataFrame:
    """
    Фильтрует реальные данные по месяцу указанной даты.
    """
    try:
        # Преобразуем дату
        current_date = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        start_of_month = current_date.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')

        df_copy = df_copy.dropna(subset=['date'])

        # Фильтруем по месяцу
        filtered_df = df_copy[
            (df_copy['date'] >= start_of_month) &
            (df_copy['date'] <= current_date)
            ]

        logger.info(
            f"Отфильтровано {len(filtered_df)} реальных транзакций за период "
            f"с {start_of_month.date()} по {current_date.date()}"
        )
        return filtered_df
    except Exception as e:
        logger.error(f"Ошибка при фильтрации данных по месяцу: {e}")
        return df


def main_page(date_time: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Генерирует JSON-ответ для главной страницы на основе реальных данных.
    """
    try:
        print(f"Формирование главной страницы с реальными данными для даты: {date_time}")

        settings = load_user_settings()

        # Фильтрация реальных данных по текущему месяцу
        filtered_df = filter_data_by_month(df, date_time)

        # Получение реальной статистики
        cards_stats = calculate_card_stats(filtered_df)
        top_transactions = get_top_transactions(filtered_df)

        # Получаем реальные данные через API
        currency_rates = get_currency_rates(settings.get("user_currencies", []))
        stock_prices = get_stock_prices(settings.get("user_stocks", []))

        # Формирование ответа с реальными данными
        response = {
            "greeting": get_greeting(date_time),
            "cards": cards_stats,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }

        print(
            f"Сформирован ответ с реальными данными: {len(cards_stats)} карт, "
            f"{len(top_transactions)} топ-транзакций"
        )
        print(f"Курсы валют: {len(currency_rates)}, Цены акций: {len(stock_prices)}")
        return response
    except Exception as e:
        logger.error(f"Ошибка при формировании главной страницы с реальными данными: {e}")
        return {
            "greeting": "Добрый день",
            "cards": [],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": []
        }
