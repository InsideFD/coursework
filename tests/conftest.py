import pytest
import pandas as pd


@pytest.fixture
def sample_transactions():
    """Фикстура с примером транзакций для тестирования."""
    return [
        {"description": "Покупка в магазине", "category": "Продукты", "amount": 100},
        {"description": "Оплата услуг", "category": "Коммунальные услуги", "amount": 200},
        {"description": "Покупка в Apple Store", "category": "Развлечения", "amount": 300}
    ]


@pytest.fixture
def sample_dataframe():
    """Фикстура с примером DataFrame для тестирования."""
    data = {
        'date': ['2023-01-01', '2023-01-15', '2023-02-01', '2023-02-15', '2023-03-01'],
        'amount': [100.50, 250.75, 50.25, 300.00, 75.30],
        'card_number': [
            '1234567812345678', '1234567812345678', '8765432187654321',
            '1234567812345678', '8765432187654321'
        ],
        'category': ['Продукты', 'Транспорт', 'Развлечения', 'Продукты', 'Кафе'],
        'description': ['Покупка в магазине', 'Такси', 'Кино', 'Супермаркет', 'Кофе']
    }
    return pd.DataFrame(data)
