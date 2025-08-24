import re


class RootClass:
    """Родительский класс с базовой валидацией."""

    def validate(self, *args):
        """
        Проверяет, что ни одно из переданных значений не пустое.

        Parameters
        ----------
        *args : tuple
            Переменное количество аргументов для проверки.

        Raises
        ------
        ValueError
            Если хотя бы один аргумент пустой.
        """
        for value in args:
            if value is None or (isinstance(value, str) and value.strip() == ''):
                raise ValueError("Все поля должны быть заполнены")


class Client(RootClass):
    """Класс для представления клиента."""

    def __init__(self, id, name, email, phone, city, address):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.city = city
        self.address = address

    def validate_all(self):
        """Проверяет все поля клиента."""
        super().validate(self.name, self.email, self.phone, self.city, self.address)

        # Проверка email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Неверный формат email")

        # Проверка телефона
        if not re.match(r"^\+?[0-9]{10,15}$", self.phone):
            raise ValueError("Неверный формат телефона")


class Product(RootClass):
    """Класс для представления товара."""

    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = float(price)

    def validate_all(self):
        """Проверяет все поля товара."""
        super().validate(self.name)

        if self.price <= 0:
            raise ValueError("Цена должна быть положительным числом")


class Order(RootClass):
    """Класс для представления заказа."""

    def __init__(self, id, client_id, total_amount, order_date, items=None):
        self.id = id
        self.client_id = client_id
        self.total_amount = float(total_amount)
        self.order_date = order_date
        self.items = items if items else []

    def validate_all(self):
        """Проверяет все поля заказа."""
        super().validate(self.client_id, self.order_date)

        if self.total_amount < 0:
            raise ValueError("Сумма заказа не может быть отрицательной")