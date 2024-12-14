import os
import csv
import html

class PriceMachine:
    def __init__(self):
        self.data = []  # Хранит загруженные данные
        self.result = ''  # Хранит последний результат поиска
        self.name_length = 0  # Максимальная длина имени для выравнивания

    def load_prices(self, file_path='.'):
        """
        Сканирует указанный каталог. Ищет файлы со словом 'price' в названии.
        Загружает данные из файлов, учитывая только столбцы с названием, ценой и весом.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Директория {file_path} не найдена.")

        valid_product_headers = {"товар", "название", "наименование", "продукт"}
        valid_price_headers = {"цена", "розница"}
        valid_weight_headers = {"вес", "масса", "фасовка"}

        for filename in os.listdir(file_path):
            if "price" in filename.lower():
                filepath = os.path.join(file_path, filename)
                with open(filepath, encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=',')
                    headers = next(reader)

                    product_idx = self._search_column(headers, valid_product_headers)
                    price_idx = self._search_column(headers, valid_price_headers)
                    weight_idx = self._search_column(headers, valid_weight_headers)

                    if product_idx is not None and price_idx is not None and weight_idx is not None:
                        for row in reader:
                            try:
                                product = row[product_idx].strip()
                                price = float(row[price_idx])
                                weight = float(row[weight_idx])
                                price_per_kg = price / weight
                                self.data.append({
                                    "product": product,
                                    "price": price,
                                    "weight": weight,
                                    "filename": filename,
                                    "price_per_kg": price_per_kg
                                })
                            except (ValueError, IndexError):
                                continue

    def _search_column(self, headers, valid_names):
        """
        Возвращает индекс первого столбца, соответствующего одному из допустимых имен.
        """
        for i, header in enumerate(headers):
            if header.lower() in valid_names:
                return i
        return None

    def export_to_html(self, fname='output.html'):
        """
        Экспортирует текущий массив данных в HTML-файл.
        """
        rows = []
        for i, item in enumerate(self.data, start=1):
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td>{html.escape(item['product'])}</td>
                <td>{item['price']}</td>
                <td>{item['weight']}</td>
                <td>{html.escape(item['filename'])}</td>
                <td>{item['price_per_kg']:.2f}</td>
            </tr>
            """)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Прайс-листы</title>
        </head>
        <body>
            <h1>Позиции продуктов</h1>
            <table border="1">
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
                {''.join(rows)}
            </table>
        </body>
        </html>
        """
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def find_text(self, text):
        """
        Ищет товары по фрагменту названия и возвращает отсортированный список позиций.
        """
        filtered_data = [
            item for item in self.data if text.lower() in item['product'].lower()
        ]
        sorted_data = sorted(filtered_data, key=lambda x: x['price_per_kg'])
        self.result = sorted_data

        print("\n№   Наименование               цена вес   файл   цена за кг.")
        for i, item in enumerate(sorted_data, start=1):
            print(f"{i:<3} {item['product']:<25} {item['price']:<5} {item['weight']:<4} {item['filename']:<10} {item['price_per_kg']:.2f}")

# Логика работы программы
pm = PriceMachine()

try:
    pm.load_prices()
    print("Данные загружены.")
except Exception as e:
    print(f"Ошибка: {e}")
    exit()

while True:
    query = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
    if query.lower() == 'exit':
        print("Работа программы завершена.")
        break
    pm.find_text(query)

print("Экспорт данных в HTML...")
pm.export_to_html()
print("Данные экспортированы в файл 'output.html'.")
