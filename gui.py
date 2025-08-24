import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db import Database
from models import Client, Product, Order
import datetime
from analysis import Analysis


class Application(tk.Tk):
    """ Окно приложения."""

    def __init__(self):
        super().__init__()
        self.title("MANAGER APP")
        self.geometry("1200x700")

        self.db = Database()
        self.analysis = Analysis(self.db)
        self.current_order_items = []  # Товары в текущем заказе [(product_id, quantity)]

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Создает интерфейс приложения."""
        # Создаем вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Вкладки
        self.client_frame = ttk.Frame(self.notebook)
        self.product_frame = ttk.Frame(self.notebook)
        self.order_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.client_frame, text="Клиенты")
        self.notebook.add(self.product_frame, text="Товары")
        self.notebook.add(self.order_frame, text="Заказы")
        self.notebook.add(self.analysis_frame, text="Аналитика")

        self.setup_client_tab()
        self.setup_product_tab()
        self.setup_order_tab()
        self.setup_analysis_tab()

    def setup_client_tab(self):
        """Создает вкладку клиентов."""
        # Фрейм для формы добавления клиента
        form_frame = ttk.LabelFrame(self.client_frame, text="Добавить клиента")
        form_frame.pack(fill='x', padx=10, pady=5)

        # Поля ввода
        fields = ['Имя', 'Email', 'Телефон', 'Город', 'Адрес']
        self.client_entries = {}

        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=field).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            self.client_entries[field.lower()] = entry

        # кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить клиента", command=self.add_client).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить поля", command=self.clear_client_fields).pack(side='left', padx=5)

        # фрейм поиск и управление
        search_frame = ttk.LabelFrame(self.client_frame, text="Поиск и управление")
        search_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(search_frame, text="Поиск:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.client_search_entry = ttk.Entry(search_frame, width=30)
        self.client_search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.client_search_entry.bind('<KeyRelease>', lambda e: self.load_clients())

        ttk.Button(search_frame, text="Удалить выбранного", command=self.delete_client).grid(row=0, column=2, padx=5,
                                                                                             pady=5)
        ttk.Button(search_frame, text="Экспорт в CSV", command=lambda: self.export_data('clients')).grid(row=0,
                                                                                                         column=3,
                                                                                                         padx=5, pady=5)
        ttk.Button(search_frame, text="Импорт из CSV", command=lambda: self.import_data('clients')).grid(row=0,
                                                                                                         column=4,
                                                                                                         padx=5, pady=5)

        ttk.Button(search_frame, text="Экспорт в JSON", command=lambda: self.export_data_json('clients')).grid(row=0,
                                                                                                               column=5,
                                                                                                               padx=5,
                                                                                                               pady=5)

        ttk.Button(search_frame, text="Импорт из JSON", command=lambda: self.import_data_json('clients')).grid(row=0,
                                                                                                               column=6,
                                                                                                               padx=5,
                                                                                                               pady=5)

        # таблтица клиентов
        table_frame = ttk.Frame(self.client_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Имя', 'Email', 'Телефон', 'Город', 'Адрес')
        self.client_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.client_tree.heading(col, text=col)
            self.client_tree.column(col, width=120)

        # полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.client_tree.yview)
        self.client_tree.configure(yscroll=scrollbar.set)

        self.client_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_product_tab(self):
        """Создает вкладку товаров."""
        # Фрейм для формы добавления товара
        form_frame = ttk.LabelFrame(self.product_frame, text="Добавить товар")
        form_frame.pack(fill='x', padx=10, pady=5)

        # поля ввода
        fields = ['Наименование', 'Цена']
        self.product_entries = {}

        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=field).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            self.product_entries[field.lower()] = entry

        # кнопки
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить товар", command=self.add_product).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить поля", command=self.clear_product_fields).pack(side='left', padx=5)

        # Фрейм поиска и управления
        search_frame = ttk.LabelFrame(self.product_frame, text="Поиск и управление")
        search_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(search_frame, text="Поиск:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.product_search_entry = ttk.Entry(search_frame, width=30)
        self.product_search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.product_search_entry.bind('<KeyRelease>', lambda e: self.load_products())

        ttk.Button(search_frame, text="Удалить выбранный", command=self.delete_product).grid(row=0, column=2, padx=5,
                                                                                             pady=5)
        ttk.Button(search_frame, text="Экспорт в CSV", command=lambda: self.export_data('products')).grid(row=0,
                                                                                                          column=3,
                                                                                                          padx=5,
                                                                                                          pady=5)
        ttk.Button(search_frame, text="Импорт из CSV", command=lambda: self.import_data('products')).grid(row=0,
                                                                                                          column=4,
                                                                                                          padx=5,
                                                                                                          pady=5)

        ttk.Button(search_frame, text="Экспорт в JSON", command=lambda: self.export_data_json('products')).grid(row=0,
                                                                                                               column=5,
                                                                                                               padx=5,
                                                                                                               pady=5)

        ttk.Button(search_frame, text="Импорт из JSON", command=lambda: self.import_data_json('products')).grid(row=0,
                                                                                                               column=6,
                                                                                                               padx=5,
                                                                                                               pady=5)

        # Таблица товаров
        table_frame = ttk.Frame(self.product_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Наименование', 'Цена')
        self.product_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=120)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscroll=scrollbar.set)

        self.product_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_order_tab(self):
        """Создает вкладку заказов."""
        # Фрейм для формы создания заказа
        form_frame = ttk.LabelFrame(self.order_frame, text="Создать заказ")
        form_frame.pack(fill='x', padx=10, pady=5)

        # Выбор клиента
        ttk.Label(form_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(form_frame, textvariable=self.client_var, state="readonly", width=27)
        self.client_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Выбор товара и количества
        ttk.Label(form_frame, text="Товар:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(form_frame, textvariable=self.product_var, state="readonly", width=27)
        self.product_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Количество:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_spin = ttk.Spinbox(form_frame, from_=1, to=100, textvariable=self.quantity_var, width=10)
        self.quantity_spin.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        # Кнопки для управления заказом
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="Добавить товар", command=self.add_to_order).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить товар", command=self.remove_from_order).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Оформить заказ", command=self.create_order).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить заказ", command=self.clear_order).pack(side='left', padx=5)

        # Таблица товаров в заказе
        ttk.Label(form_frame, text="Товары в заказе:").grid(row=3, column=0, padx=5, pady=5, sticky='w')

        order_items_frame = ttk.Frame(form_frame)
        order_items_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky='we')

        columns = ('ID', 'Наименование', 'Цена', 'Количество', 'Сумма')
        self.order_tree = ttk.Treeview(order_items_frame, columns=columns, show='headings', height=5)

        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=100)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(order_items_frame, orient=tk.VERTICAL, command=self.order_tree.yview)
        self.order_tree.configure(yscroll=scrollbar.set)

        self.order_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Итоговая сумма
        ttk.Label(form_frame, text="Итоговая сумма:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.total_var = tk.StringVar(value="0.00")
        ttk.Label(form_frame, textvariable=self.total_var, font=('Arial', 10, 'bold')).grid(row=5, column=1, padx=5,
                                                                                            pady=5, sticky='w')

        # Фрейм поиска и управления заказами
        search_frame = ttk.LabelFrame(self.order_frame, text="Поиск и управление заказами")
        search_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(search_frame, text="Поиск:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.order_search_entry = ttk.Entry(search_frame, width=30)
        self.order_search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.order_search_entry.bind('<KeyRelease>', lambda e: self.load_orders())

        ttk.Button(search_frame, text="Удалить выбранный", command=self.delete_order).grid(row=0, column=2, padx=5,
                                                                                           pady=5)
        ttk.Button(search_frame, text="Экспорт в CSV", command=lambda: self.export_data('orders')).grid(row=0, column=3,
                                                                                                        padx=5, pady=5)
        ttk.Button(search_frame, text="Импорт из CSV", command=lambda: self.import_data('orders')).grid(row=0, column=4,
                                                                                                        padx=5, pady=5)

        # Таблица заказов
        table_frame = ttk.Frame(self.order_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'ID клиента', 'Сумма', 'Дата заказа')
        self.orders_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=120)

        # Привязываем двойной клик для просмотра деталей заказа
        self.orders_tree.bind('<Double-1>', self.show_order_details)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscroll=scrollbar.set)

        self.orders_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def setup_analysis_tab(self):
        """Создает вкладку аналитики."""
        # Кнопки для анализа
        button_frame = ttk.Frame(self.analysis_frame)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Топ 5 клиентов", command=self.show_top_clients).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Динамика заказов", command=self.show_orders_dynamics).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Граф связей клиентов", command=self.show_client_connections).pack(side='left',
                                                                                                         padx=5)

        # Фрейм для отображения графиков
        self.analysis_frame_inner = ttk.Frame(self.analysis_frame)
        self.analysis_frame_inner.pack(fill='both', expand=True, padx=10, pady=10)

    def load_data(self):
        """Загружает данные во все таблицы."""
        self.load_clients()
        self.load_products()
        self.load_orders()
        self.update_client_combo()
        self.update_product_combo()

    def load_clients(self):
        """Загружает клиентов в таблицу."""
        search_term = self.client_search_entry.get()
        clients = self.db.get_clients(search_term)

        self.client_tree.delete(*self.client_tree.get_children())
        for client in clients:
            self.client_tree.insert('', 'end', values=(
                client.id, client.name, client.email,
                client.phone, client.city, client.address
            ))

    def load_products(self):
        """Загружает товары в таблицу."""
        search_term = self.product_search_entry.get()
        products = self.db.get_products(search_term)

        self.product_tree.delete(*self.product_tree.get_children())
        for product in products:
            self.product_tree.insert('', 'end', values=(
                product.id, product.name, product.price
            ))

    def load_orders(self):
        """Загружает заказы в таблицу."""
        search_term = self.order_search_entry.get()
        orders = self.db.get_orders(search_term)

        self.orders_tree.delete(*self.orders_tree.get_children())
        for order in orders:
            self.orders_tree.insert('', 'end', values=(
                order.id, order.client_id, order.total_amount, order.order_date
            ))

    def update_client_combo(self):
        """Обновляет выпадающий список клиентов."""
        clients = self.db.get_clients()
        client_values = [f"{client.id} - {client.name}" for client in clients]
        self.client_combo['values'] = client_values
        if client_values:
            self.client_combo.current(0)

    def update_product_combo(self):
        """Обновляет выпадающий список товаров."""
        products = self.db.get_products()
        product_values = [f"{product.id} - {product.name} ({product.price} руб.)" for product in products]
        self.product_combo['values'] = product_values
        if product_values:
            self.product_combo.current(0)

    def add_client(self):
        """Добавляет нового клиента."""
        try:
            # Генерируем ID
            clients = self.db.get_clients()
            new_id = f"CLT{len(clients) + 1:03d}"

            # Получаем данные из полей ввода
            name = self.client_entries['имя'].get()
            email = self.client_entries['email'].get()
            phone = self.client_entries['телефон'].get()
            city = self.client_entries['город'].get()
            address = self.client_entries['адрес'].get()

            # Создаем клиента и валидируем
            client = Client(new_id, name, email, phone, city, address)
            client.validate_all()

            # Добавляем в базу
            self.db.add_client(client)
            self.load_clients()
            self.update_client_combo()

            # Очищаем поля ввода
            self.clear_client_fields()

            messagebox.showinfo("Успех", "Клиент успешно добавлен")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_product(self):
        """Добавляет новый товар."""
        try:
            # Генерируем ID
            products = self.db.get_products()
            new_id = f"PRD{len(products) + 1:03d}"

            # Получаем данные из полей ввода
            name = self.product_entries['наименование'].get()
            price = self.product_entries['цена'].get()

            # Создаем товар и валидируем
            product = Product(new_id, name, price)
            product.validate_all()

            # Добавляем в базу
            self.db.add_product(product)
            self.load_products()
            self.update_product_combo()

            # Очищаем поля ввода
            self.clear_product_fields()

            messagebox.showinfo("Успех", "Товар успешно добавлен")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_to_order(self):
        """Добавляет товар в текущий заказ."""
        try:
            # Получаем выбранный товар
            product_str = self.product_var.get()
            if not product_str:
                messagebox.showwarning("Предупреждение", "Выберите товар")
                return

            # Извлекаем ID товара из строки
            product_id = product_str.split(' - ')[0]

            # Получаем количество
            quantity = int(self.quantity_var.get())

            # Находим товар в базе
            products = self.db.get_products()
            product = next((p for p in products if p.id == product_id), None)

            if not product:
                messagebox.showerror("Ошибка", "Товар не найден")
                return

            # Проверяем, не добавлен ли уже этот товар
            for i, (p_id, qty) in enumerate(self.current_order_items):
                if p_id == product_id:
                    # Обновляем количество
                    self.current_order_items[i] = (product_id, qty + quantity)
                    break
            else:
                # Добавляем новый товар
                self.current_order_items.append((product_id, quantity))

            # Обновляем таблицу товаров в заказе
            self.update_order_items_table()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def remove_from_order(self):
        """Удаляет товар из текущего заказа."""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return

        # Получаем ID товара
        item = self.order_tree.item(selected[0])
        product_id = item['values'][0]

        # Удаляем товар из заказа
        self.current_order_items = [(p_id, qty) for p_id, qty in self.current_order_items if p_id != product_id]

        # Обновляем таблицу
        self.update_order_items_table()

    def create_order(self):
        """Создает новый заказ."""
        try:
            # Проверяем, выбран ли клиент
            client_str = self.client_var.get()
            if not client_str:
                messagebox.showwarning("Предупреждение", "Выберите клиента")
                return

            # Проверяем, есть ли товары в заказе
            if not self.current_order_items:
                messagebox.showwarning("Предупреждение", "Добавьте товары в заказ")
                return

            # Извлекаем ID клиента из строки
            client_id = client_str.split(' - ')[0]

            # Генерируем ID заказа
            orders = self.db.get_orders()
            new_id = f"ORD{len(orders) + 1:03d}"

            # Получаем текущую дату
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Создаем заказ
            order = Order(new_id, client_id, self.calculate_order_total(), current_date, self.current_order_items)
            order.validate_all()

            # Добавляем в базу
            self.db.add_order(order)
            self.load_orders()

            # Очищаем текущий заказ
            self.clear_order()

            messagebox.showinfo("Успех", "Заказ успешно создан")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def calculate_order_total(self):
        """Рассчитывает общую сумму заказа."""
        total = 0
        products = self.db.get_products()

        for product_id, quantity in self.current_order_items:
            product = next((p for p in products if p.id == product_id), None)
            if product:
                total += product.price * quantity

        return total

    def update_order_items_table(self):
        """Обновляет таблицу товаров в заказе."""
        self.order_tree.delete(*self.order_tree.get_children())

        products = self.db.get_products()
        total = 0

        for product_id, quantity in self.current_order_items:
            product = next((p for p in products if p.id == product_id), None)
            if product:
                item_total = product.price * quantity
                total += item_total

                self.order_tree.insert('', 'end', values=(
                    product.id, product.name, product.price, quantity, item_total
                ))

        # Обновляем итоговую сумму
        self.total_var.set(f"{total:.2f}")

    def show_order_details(self, event):
        """Показывает детали выбранного заказа."""
        selected = self.orders_tree.selection()
        if not selected:
            return

        # Получаем ID заказа
        order_id = self.orders_tree.item(selected[0])['values'][0]

        # Получаем товары заказа
        items = self.db.get_order_items(order_id)

        # Создаем окно с деталями
        details_window = tk.Toplevel(self)
        details_window.title(f"Детали заказа {order_id}")
        details_window.geometry("600x400")

        # Таблица товаров
        columns = ('ID', 'Наименование', 'Цена', 'Количество', 'Сумма')
        tree = ttk.Treeview(details_window, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Заполняем таблицу
        total = 0
        for item in items:
            item_total = item[2] * item[3]
            total += item_total
            tree.insert('', 'end', values=item + (item_total,))

        tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Итоговая сумма
        ttk.Label(details_window, text=f"Итоговая сумма: {total:.2f} руб.", font=('Arial', 10, 'bold')).pack(pady=5)

    def delete_client(self):
        """Удаляет выбранного клиента."""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return

        client_id = self.client_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого клиента?"):
            self.db.delete_client(client_id)
            self.load_clients()
            self.update_client_combo()

    def delete_product(self):
        """Удаляет выбранный товар."""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return

        product_id = self.product_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот товар?"):
            self.db.delete_product(product_id)
            self.load_products()
            self.update_product_combo()

    def delete_order(self):
        """Удаляет выбранный заказ."""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")
            return

        order_id = self.orders_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот заказ?"):
            self.db.delete_order(order_id)
            self.load_orders()

    def export_data(self, table_name):
        """Экспортирует данные в CSV."""
        filename = f"{table_name}_export.csv"
        self.db.export_to_csv(table_name, filename)
        messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")

    def import_data(self, table_name):
        """Импортирует данные из CSV."""
        filename = f"{table_name}_import.csv"
        self.db.import_from_csv(table_name, filename)

    def export_data_json(self, table_name):
        """Экспортирует данные в JSON."""
        filename = f"{table_name}_export.json"
        self.db.export_to_json(table_name, filename)
        messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")

    def import_data_json(self, table_name):
        """Импортирует данные из JSON."""
        filename = f"{table_name}_import.json"

        try:
            if table_name == 'clients':
                self.db.import_clients_from_json(filename)
                self.load_clients()
                self.update_client_combo()
            elif table_name == 'products':
                self.db.import_products_from_json(filename)
                self.load_products()
                self.update_product_combo()

            messagebox.showinfo("Успех", f"Данные импортированы из {filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")

        # Обновляем данные
        if table_name == 'clients':
            self.load_clients()
            self.update_client_combo()
        elif table_name == 'products':
            self.load_products()
            self.update_product_combo()
        elif table_name == 'orders':
            self.load_orders()

        messagebox.showinfo("Успех", f"Данные импортированы из {filename}")

    def show_top_clients(self):
        """Показывает топ-5 клиентов."""
        self.analysis.show_top_clients(self.analysis_frame_inner)

    def show_orders_dynamics(self):
        """Показывает динамику заказов."""
        self.analysis.show_orders_dynamics(self.analysis_frame_inner)

    def show_client_connections(self):
        """Показывает граф связей клиентов."""
        self.analysis.show_client_connections(self.analysis_frame_inner)

    def clear_client_fields(self):
        """Очищает поля ввода клиента."""
        for entry in self.client_entries.values():
            entry.delete(0, tk.END)

    def clear_product_fields(self):
        """Очищает поля ввода товара."""
        for entry in self.product_entries.values():
            entry.delete(0, tk.END)

    def clear_order(self):
        """Очищает текущий заказ."""
        self.current_order_items = []
        self.update_order_items_table()
        self.client_var.set('')
        if self.client_combo['values']:
            self.client_combo.current(0)