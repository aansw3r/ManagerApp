import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import networkx as nx
from db import Database


class Analysis:
    """Класс для анализа и визуализации данных."""

    def __init__(self, db):
        self.db = db

    def show_top_clients(self, parent_frame):
        """Показывает топ-5 клиентов по количеству заказов."""
        # Очищаем предыдущий график
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Получаем данные
        top_clients = self.db.get_top_clients()

        if not top_clients:
            return

        # Создаем DataFrame
        df = pd.DataFrame(top_clients, columns=['ID', 'Имя', 'Количество заказов'])

        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(df['Имя'], df['Количество заказов'])
        ax.set_title('Топ клиентов по количеству заказов')
        ax.set_ylabel('Количество заказов')
        ax.tick_params(axis='x', rotation=45)

        # Встраиваем график в интерфейс
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_orders_dynamics(self, parent_frame):
        """Показывает динамику заказов по датам."""
        # Очищаем предыдущий график
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Получаем данные
        dynamics = self.db.get_orders_dynamics()

        if not dynamics:
            return

        # Создаем DataFrame
        df = pd.DataFrame(dynamics, columns=['Дата', 'Количество заказов', 'Общая сумма'])

        # Создаем график
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # График количества заказов
        ax1.plot(df['Дата'], df['Количество заказов'], marker='o')
        ax1.set_title('Динамика количества заказов')
        ax1.set_ylabel('Количество заказов')
        ax1.tick_params(axis='x', rotation=45)

        # График общей суммы
        ax2.plot(df['Дата'], df['Общая сумма'], marker='o', color='orange')
        ax2.set_title('Динамика суммы заказов')
        ax2.set_ylabel('Сумма заказов')
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()

        # Встраиваем график в интерфейс
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_client_connections(self, parent_frame):
        """Показывает граф связей клиентов."""
        # Очищаем предыдущий график
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Получаем данные
        clients = self.db.get_clients()
        orders = self.db.get_orders()

        if not clients or not orders:
            return

        # Создаем граф
        G = nx.Graph()

        # Добавляем узлы (клиентов)
        for client in clients:
            G.add_node(client.id, label=client.name, city=client.city)

        # Добавляем связи (общие заказы)
        # В этом примере просто связываем клиентов из одного города
        city_groups = {}
        for client in clients:
            if client.city not in city_groups:
                city_groups[client.city] = []
            city_groups[client.city].append(client.id)

        for city, client_ids in city_groups.items():
            if len(client_ids) > 1:
                for i in range(len(client_ids)):
                    for j in range(i + 1, len(client_ids)):
                        if G.has_edge(client_ids[i], client_ids[j]):
                            G[client_ids[i]][client_ids[j]]['weight'] += 1
                        else:
                            G.add_edge(client_ids[i], client_ids[j], weight=1)

        # Рисуем граф
        fig, ax = plt.subplots(figsize=(10, 8))

        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)
        nx.draw_networkx_edges(G, pos, edge_color='gray')
        nx.draw_networkx_labels(G, pos, labels={node: data['label'] for node, data in G.nodes(data=True)})

        ax.set_title('Граф связей клиентов (по городам)')
        ax.axis('off')

        # Встраиваем график в интерфейс
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)