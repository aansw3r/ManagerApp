import sqlite3
import json
import csv
from models import Client, Product, Order


class Database:
    """Класс для работы с базой данных SQLite."""

    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Создает и возвращает соединение с базой данных."""
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Инициализирует таблицы в базе данных."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица клиентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                city TEXT NOT NULL,
                address TEXT NOT NULL
            )
        ''')

        # Таблица товаров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')

        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                total_amount REAL NOT NULL,
                order_date TEXT NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')

        # Таблица товаров в заказах
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        conn.commit()
        conn.close()

    # Методы для работы с клиентами
    def add_client(self, client):
        """Добавляет клиента в базу данных."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clients VALUES (?, ?, ?, ?, ?, ?)",
            (client.id, client.name, client.email, client.phone, client.city, client.address)
        )
        conn.commit()
        conn.close()

    def get_clients(self, search_term=""):
        """Возвращает всех клиентов с возможностью фильтрации."""
        conn = self.get_connection()
        cursor = conn.cursor()

        if search_term:
            cursor.execute(
                "SELECT * FROM clients WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR city LIKE ? OR address LIKE ?",
                (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
            )
        else:
            cursor.execute("SELECT * FROM clients")

        clients = [Client(*row) for row in cursor.fetchall()]
        conn.close()
        return clients

    def delete_client(self, client_id):
        """Удаляет клиента по ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
        conn.commit()
        conn.close()

    # Методы для работы с товарами
    def add_product(self, product):
        """Добавляет товар в базу данных."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products VALUES (?, ?, ?)",
            (product.id, product.name, product.price)
        )
        conn.commit()
        conn.close()

    def get_products(self, search_term=""):
        """Возвращает все товары с возможностью фильтрации."""
        conn = self.get_connection()
        cursor = conn.cursor()

        if search_term:
            cursor.execute(
                "SELECT * FROM products WHERE name LIKE ? OR id LIKE ?",
                (f"%{search_term}%", f"%{search_term}%")
            )
        else:
            cursor.execute("SELECT * FROM products")

        products = [Product(*row) for row in cursor.fetchall()]
        conn.close()
        return products

    def delete_product(self, product_id):
        """Удаляет товар по ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()

    # Методы для работы с заказами
    def add_order(self, order):
        """Добавляет заказ в базу данных."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Добавляем заказ
        cursor.execute(
            "INSERT INTO orders VALUES (?, ?, ?, ?)",
            (order.id, order.client_id, order.total_amount, order.order_date)
        )

        # Добавляем товары заказа
        for product_id, quantity in order.items:
            cursor.execute(
                "INSERT INTO order_items VALUES (?, ?, ?)",
                (order.id, product_id, quantity)
            )

        conn.commit()
        conn.close()

    def get_orders(self, search_term=""):
        """Возвращает все заказы с возможностью фильтрации."""
        conn = self.get_connection()
        cursor = conn.cursor()

        if search_term:
            cursor.execute('''
                SELECT o.* FROM orders o
                JOIN clients c ON o.client_id = c.id
                WHERE c.name LIKE ? OR o.id LIKE ? OR o.order_date LIKE ? OR o.total_amount LIKE ?
            ''', (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        else:
            cursor.execute("SELECT * FROM orders")

        orders = []
        for row in cursor.fetchall():
            order_id = row[0]
            # Получаем товары для этого заказа
            cursor.execute('''
                SELECT p.id, p.name, p.price, oi.quantity 
                FROM products p
                JOIN order_items oi ON p.id = oi.product_id
                WHERE oi.order_id = ?
            ''', (order_id,))
            items = cursor.fetchall()
            orders.append(Order(row[0], row[1], row[2], row[3], items))

        conn.close()
        return orders

    def delete_order(self, order_id):
        """Удаляет заказ по ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Сначала удаляем связанные товары
        cursor.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
        # Затем удаляем заказ
        cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))

        conn.commit()
        conn.close()

    def get_order_items(self, order_id):
        """Возвращает товары для конкретного заказа."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT p.id, p.name, p.price, oi.quantity 
            FROM products p
            JOIN order_items oi ON p.id = oi.product_id
            WHERE oi.order_id = ?
        ''', (order_id,))

        items = cursor.fetchall()
        conn.close()
        return items

    # Методы для импорта/экспорта
    def export_to_csv(self, table_name, filename):
        """Экспортирует данные из указанной таблицы в CSV."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Записываем заголовки
            writer.writerow([description[0] for description in cursor.description])
            # Записываем данные
            writer.writerows(rows)

        conn.close()

    def import_from_csv(self, table_name, filename):
        """Импортирует данные из CSV в указанную таблицу."""
        conn = self.get_connection()
        cursor = conn.cursor()

        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Пропускаем заголовок

            for row in reader:
                placeholders = ', '.join(['?' for _ in row])
                cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

        conn.commit()
        conn.close()

    def export_to_json(self, table_name, filename):
        """Экспортирует данные из указанной таблицы в JSON."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

        data = []
        for row in rows:
            data.append(dict(zip(column_names, row)))

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        conn.close()

    def import_clients_from_json(self, filename):
        """Импортирует клиентов из JSON с генерацией новых ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

            # Получаем текущее количество клиентов
            clients_count = len(self.get_clients())

            for i, item in enumerate(data, 1):
                try:
                    # Генерируем новый ID
                    new_id = f"CLT{clients_count + i:03d}"

                    cursor.execute(
                        "INSERT INTO clients (id, name, email, phone, city, address) VALUES (?, ?, ?, ?, ?, ?)",
                        (new_id, item['name'], item['email'], item['phone'], item['city'], item['address'])
                    )

                except Exception as e:
                    print(f"Ошибка при импорте клиента: {e}")
                    continue

        conn.commit()
        conn.close()

    def import_products_from_json(self, filename):
        """Импортирует товары из JSON с генерацией новых ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

            # Получаем текущее количество товаров
            products_count = len(self.get_products())

            for i, item in enumerate(data, 1):
                try:
                    # Генерируем новый ID
                    new_id = f"PRD{products_count + i:03d}"

                    cursor.execute(
                        "INSERT INTO products (id, name, price) VALUES (?, ?, ?)",
                        (new_id, item['name'], item['price'])
                    )

                except Exception as e:
                    print(f"Ошибка при импорте товара: {e}")
                    continue

        conn.commit()
        conn.close()

    # Методы для анализа данных
    def get_top_clients(self, limit=5):
        """Возвращает топ клиентов по количеству заказов."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.id, c.name, COUNT(o.id) as order_count
            FROM clients c
            JOIN orders o ON c.id = o.client_id
            GROUP BY c.id, c.name
            ORDER BY order_count DESC
            LIMIT ?
        ''', (limit,))

        result = cursor.fetchall()
        conn.close()
        return result

    def get_orders_dynamics(self):
        """Возвращает динамику заказов по датам."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT order_date, COUNT(id) as order_count, SUM(total_amount) as total_amount
            FROM orders
            GROUP BY order_date
            ORDER BY order_date
        ''')

        result = cursor.fetchall()
        conn.close()
        return result