import logging
from typing import Any, Dict, List

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Выполняет поиск транзакций по запросу.

    Args:
        query: строка для поиска
        transactions: список транзакций в формате словарей

    Returns:
        Список найденных транзакций
    """
    try:
        results = []

        for transaction in transactions:
            # Поиск в описании и категории
            if (
                query.lower() in transaction.get("description", "").lower()
                or query.lower() in transaction.get("category", "").lower()
            ):
                results.append(transaction)

        logger.info(f"Найдено {len(results)} транзакций по запросу '{query}'")
        return results
    except Exception as e:
        logger.error(f"Ошибка при выполнении поиска: {e}")
        return []
