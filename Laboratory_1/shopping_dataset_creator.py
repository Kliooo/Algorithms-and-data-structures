import random
import shutil
from datetime import datetime, timedelta
from openpyxl import Workbook

stores = []
with open('stores.txt', 'r', encoding='utf-8') as file:
    for line in file:
        parts = line.strip().split(';')
        if len(parts) == 5:
            store_name = parts[0].strip()
            lat = float(parts[1].strip())
            lon = float(parts[2].strip())
            open_time = parts[3].strip()
            close_time = parts[4].strip()
            stores.append((store_name, lat, lon, open_time, close_time))

categories_and_brands = {}
with open('brands.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if ';' in line:
            parts = line.split(';')
            category = parts[0].strip()
            brands_list = [brand.strip() for brand in parts[1:-1]]
            average_price = float(parts[-1].strip())
            categories_and_brands[category] = (brands_list, average_price)

store_categories = {
    "М.Видео": ['Смартфоны', 'Ноутбуки', 'Телевизоры', 'Планшеты', 'Наушники', 'Стиральные машины', 'Холодильники'],
    "Эльдорадо": ['Смартфоны', 'Ноутбуки', 'Телевизоры', 'Планшеты', 'Наушники', 'Стиральные машины', 'Холодильники'],
    "DNS": ['Смартфоны', 'Ноутбуки', 'Телевизоры', 'Планшеты', 'Наушники', 'Стиральные машины', 'Холодильники'],
    "Лента": ['Овощи', 'Фрукты', 'Шоколад', 'Молочные продукты', 'Хлебобулочные изделия', 'Кофе и чай', 'Замороженные продукты'],
    "Пятёрочка": ['Овощи', 'Фрукты', 'Шоколад', 'Молочные продукты', 'Хлебобулочные изделия', 'Кофе и чай', 'Замороженные продукты'],
    "Ашан": ['Овощи', 'Фрукты', 'Шоколад', 'Молочные продукты', 'Хлебобулочные изделия', 'Кофе и чай', 'Замороженные продукты'],
    "Hoff": ['Шкафы', 'Столы', 'Стулья', 'Диваны', 'Кровати', 'Тумбочки', 'Ванны'],
    "OBI": ['Шкафы', 'Столы', 'Стулья', 'Диваны', 'Кровати', 'Тумбочки', 'Ванны'],
    "Леруа Мерлен": ['Шкафы', 'Столы', 'Стулья', 'Диваны', 'Кровати', 'Тумбочки', 'Ванны'],
}

bin_codes = {
    "Сбербанк": ["27402", "27406", "27411", "27416", "27417", "27418", "27420", "27422", "27425", "27427"],
    "ВТБ": ["18868", "18869", "18870", "18873", "21191", "26375", "30127", "31723", "40622", "40623"],
    "ПСБ": ["02507", "04906", "24561", "24562", "24563", "26803", "26804", "29726", "29727", "29728"],
    "Газпромбанк": ["04136", "04270", "04271", "04272", "04273", "24974", "24975", "24976", "26890", "27326"],
    "Альфа-Банк": ["10584", "15400", "15428", "15429", "15481", "15482", "19539", "19540", "21118", "27714"],
}

payment_systems = {
    "МИР": "2",
    "Visa": "4",
    "MasterCard": "5",
}

def get_probabilities(probabilities_dict, entity_name):
    while True:
        probabilities = []
        print(f"Введите вероятность для каждого {entity_name} (в сумме 100):")
        for system in probabilities_dict.keys():
            prob = float(input(f"{system}: "))
            probabilities.append(prob)

        if any(prob < 0 for prob in probabilities):
            print("Ошибка: вероятность не может быть отрицательной. Пожалуйста, введите значения снова.")
        elif sum(probabilities) != 100:
            print("Ошибка: суммы вероятностей должны равняться 100. Пожалуйста, введите значения снова.")
        else:
            return probabilities

def generate_datetime(open_time, close_time):
    days_in_past = random.randint(0, 365)
    random_date = datetime.now() - timedelta(days=days_in_past)
    
    open_dt = datetime.strptime(open_time, "%H:%M").replace(year=random_date.year, month=random_date.month, day=random_date.day)
    close_dt = datetime.strptime(close_time, "%H:%M").replace(year=random_date.year, month=random_date.month, day=random_date.day)
    
    random_time = open_dt + timedelta(minutes=random.randint(0, (close_dt - open_dt).seconds // 60))

    formatted_time = random_time.strftime("%Y-%m-%dT%H:%M:%S") + "+03:00"
    
    return formatted_time

def get_coordinates(lat, lon):
    return f"{lat:.6f}, {lon:.6f}"

def choose_category_and_brand(store_name, categories_and_brands):
    available_categories = store_categories.get(store_name.strip(), [])
    category = random.choice(available_categories)
    brand = None
    if category in categories_and_brands and categories_and_brands[category]:
        brand = random.choice(categories_and_brands[category][0])

    return category, brand

def generate_card_number(bin_code, payment_system_code):
    remaining_digits = ''.join(random.choices('0123456789', k=10))

    return f"{payment_system_code}{bin_code}{remaining_digits}"

def generate_price_and_quantity(category, categories_and_brands):
    quantity = random.randint(5, 10)
    base_price = categories_and_brands.get(category, (None, 0))[1]
    price_variation = random.uniform(1, 1.005)
    price = max(round(base_price * price_variation), 1)
    total_price = price * quantity

    return quantity, total_price

def choose_bank_and_generate_card(bank_probabilities, payment_system_probabilities, card_count):
    while True:
        bank = random.choices(list(bin_codes.keys()), weights=bank_probabilities)[0]
        bin_code = random.choice(bin_codes[bank])
        payment_system = random.choices(list(payment_systems.keys()), weights=payment_system_probabilities)[0]
        card_number = generate_card_number(bin_code, payment_systems[payment_system])
        current_count = card_count.get(card_number, 0)
    
        if current_count < 5:
            card_count[card_number] = current_count + 1
            break

    return card_number

def generate_store_data(store, categories_and_brands, bank_probabilities, payment_system_probabilities, card_count):
    store_name, lat, lon, open_time, close_time = store
    coordinates = get_coordinates(lat, lon)
    visit_time = generate_datetime(open_time, close_time)

    category, brand = choose_category_and_brand(store_name, categories_and_brands)
    quantity, total_price = generate_price_and_quantity(category, categories_and_brands)
    card_number = choose_bank_and_generate_card(bank_probabilities, payment_system_probabilities, card_count)

    return [store_name.strip(), visit_time, coordinates, category, brand, card_number, quantity, total_price]

dataset = []
card_count = {}
payment_system_probabilities = get_probabilities(payment_systems, "платёжной системы")
bank_probabilities = get_probabilities(bin_codes, "банка")

while True:
    try:
        row_count = int(input("Введите количество строк для генерации (не менее 50000): "))
        if row_count < 50000:
            print("Ошибка: количество строк не должно быть меньше 50000.")
        else:
            break
    except ValueError:
        print("Ошибка: пожалуйста, введите целое число.")

for _ in range(row_count):
    store = random.choice(stores)
    dataset.append(generate_store_data(store, categories_and_brands, bank_probabilities, payment_system_probabilities, card_count))

wb = Workbook()
ws = wb.active
ws.title = "Shopping Data"

headers = ['Название магазина', 'Дата и время', 'Координаты', 'Категория', 'Бренд', 'Номер карточки', 'Количество товаров', 'Стоимость']
ws.append(headers)

column_widths = [20, 27, 25, 28, 23, 18, 20, 15]
for i, width in enumerate(column_widths, 1):
    ws.column_dimensions[chr(64 + i)].width = width

for row in dataset:
    ws.append(row)

# Сохранение файла в первой папке
original_file_path = 'shopping_dataset.xlsx'
wb.save(original_file_path)

# Указываем путь для копирования во вторую папку
backup_file_path = '../Laboratory_2/shopping_dataset.xlsx'

# Копируем файл в другую папку
shutil.copy(original_file_path, backup_file_path)

print("Генерация завершена. Данные сохранены в файл 'shopping_dataset' и дублированы в 'Laboratory_2'")
