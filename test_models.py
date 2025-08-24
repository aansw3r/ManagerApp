import unittest
import sys
import os


from models import Client, Product, Order, RootClass


class TestRootClass(unittest.TestCase):
    """Тесты для базового класса RootClass."""

    def test_validate_success(self):
        """Тест успешной валидации."""
        root = RootClass()
        root.validate("test", "value", 123, "not empty")

    def test_validate_empty_string(self):
        """Тест валидации с пустой строкой."""
        root = RootClass()
        with self.assertRaises(ValueError):
            root.validate("test", "", "value")


class TestClient(unittest.TestCase):
    """Тесты для класса Client."""

    def test_client_creation(self):
        """Тест создания клиента."""
        client = Client("CLT001", "Иван", "test@mail.com", "79161234567", "Москва", "ул. Тестовая")
        self.assertEqual(client.id, "CLT001")
        self.assertEqual(client.name, "Иван")

    def test_validate_all_success(self):
        """Тест успешной валидации клиента."""
        client = Client("CLT001", "Иван", "test@mail.com", "+79161234567", "Москва", "ул. Тестовая")
        client.validate_all()

    def test_validate_invalid_email(self):
        """Тест валидации с неверным email."""
        client = Client("CLT001", "Иван", "invalid-email", "79161234567", "Москва", "ул. Тестовая")
        with self.assertRaises(ValueError):
            client.validate_all()


class TestProduct(unittest.TestCase):
    """Тесты для класса Product."""

    def test_product_creation(self):
        """Тест создания товара."""
        product = Product("PRD001", "Телефон", 25000.0)
        self.assertEqual(product.id, "PRD001")
        self.assertEqual(product.name, "Телефон")

    def test_validate_all_success(self):
        """Тест успешной валидации товара."""
        product = Product("PRD001", "Телефон", 25000.0)
        product.validate_all()

    def test_validate_negative_price(self):
        """Тест валидации с отрицательной ценой."""
        product = Product("PRD001", "Товар", -100.0)
        with self.assertRaises(ValueError):
            product.validate_all()


class TestOrder(unittest.TestCase):
    """Тесты для класса Order."""

    def test_order_creation(self):
        """Тест создания заказа."""
        order = Order("ORD001", "CLT001", 1500.0, "2024-01-15")
        self.assertEqual(order.id, "ORD001")
        self.assertEqual(order.client_id, "CLT001")

    def test_validate_all_success(self):
        """Тест успешной валидации заказа."""
        order = Order("ORD001", "CLT001", 1000.0, "2024-01-15")
        order.validate_all()

    def test_validate_negative_amount(self):
        """Тест валидации с отрицательной суммой."""
        order = Order("ORD001", "CLT001", -1000.0, "2024-01-15")
        with self.assertRaises(ValueError):
            order.validate_all()


if __name__ == '__main__':
    unittest.main()