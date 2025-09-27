import logging
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Выполняет реальный поиск транзакций по запросу.
    """
    try:
        # Проверка входных данных
        if transactions is None:
            logger.warning("Передан None вместо списка транзакций")
            return []

        if not transactions:
            logger.info("Передан пустой список транзакций")
            return []

        if not query or not query.strip():
            logger.warning("Передан пустой запрос для поиска")
            return []

        results = []
        query_lower = query.lower().strip()
        processed_count = 0
        error_count = 0

        for transaction in transactions:
            try:
                # Безопасное получение полей
                description = str(transaction.get("description", "")).lower()
                category = str(transaction.get("category", "")).lower()

                # Поиск в описании и категории
                if query_lower in description or query_lower in category:
                    results.append(transaction)

                processed_count += 1

            except Exception as e:
                # Логируем ошибку для отдельной транзакции
                logger.warning(f"Ошибка при обработке транзакции: {e}")
                error_count += 1
                continue

        logger.info(
            f"Найдено {len(results)} транзакций по запросу '{query}'. "
            f"Обработано: {processed_count}, ошибок: {error_count}"
        )
        return results

    except Exception as e:
        # Общая ошибка (маловероятно, но на всякий случай)
        logger.error(f"Критическая ошибка при выполнении поиска: {e}")
        return []
