import random
from datetime import datetime, timedelta
from openpyxl import Workbook

stores = []
with open('store_coordinates.txt', 'r', encoding='utf-8') as file:
    for line in file:
        parts = line.strip().split(',')
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
        if ':' in line:
            parts = line.split(':')
            category = parts[0].strip()
            brands_and_price = parts[1].rsplit(';', 1)
            brands_list = [brand.strip() for brand in brands_and_price[0].split(';')]
            average_price = float(brands_and_price[1].strip())
            categories_and_brands[category] = (brands_list, average_price)

store_categories = {
    "М.Видео": ['Смартфоны', 'Ноутбуки', 'Телевизоры', 'Планшеты', 'Наушники', 'Микроволновые печи', 'Стиральные машины'],
    "Эльдорадо": ['Смартфоны', 'Ноутбуки', 'Телевизоры', 'Планшеты', 'Умные часы', 'Наушники', 'Игровые приставки', 'Блендеры'],
    "DNS": ['Смартфоны', 'Ноутбуки', 'Телевизоры', 'Планшеты', 'Кофеварки и кофемашины', 'Кондиционеры', 'Компьютерные кресла'],
    "OZON": ['Смартфоны', 'Ноутбуки', 'Телевизоры', 'Кофеварки и кофемашины', 'Холодильники', 'Гироскутеры', 'Наручные часы'],
    "Wildberries": ['Смартфоны', 'Косметика', 'Кофеварки и кофемашины', 'Холодильники', 'Микроволновые печи'],
    "Лента": ['Продукты', 'Косметика', 'Вентиляторы', 'Гироскутеры', 'Кроссовки', 'Пылесосы', 'Принтеры'],
    "Пятёрочка": ['Продукты', 'Косметика', 'Обогреватели'],
    "Ашан": ['Парфюмерия', 'Холодильники', 'Продукты'],
    "Metro": ['Продукты', 'Косметика', 'Гладильные доски', 'Стулья для офиса'],
    "O'Кей": ['Продукты', 'Косметика', 'Сейфы'],
    "Перекрёсток": ['Продукты', 'Косметика', 'Настольные лампы'],
    "Дикси": ['Продукты', 'Косметика', 'Чайники'],
    "Магнит": ['Продукты', 'Косметика', 'Чайники'],
    "FixPrice": ['Продукты', 'Косметика', 'Фены'],
    "Золотое Яблоко": ['Парфюмерия', 'Косметика', 'Ароматы', 'Сумки'],
    "Азбука Вкуса": ['Продукты'],
    "Hoff": ['Шкафы', 'Столы', 'Диваны', 'Шкафы для одежды', 'Кровати', 'Кухонные столы'],
    "OBI": ['Газонокосилки', 'Садовый инвентарь', 'Инструменты', 'Шкафы для одежды', 'Комоды', 'Кровати', 'Игровые столы', 'Камеры видеонаблюдения'],
    "Леруа Мерлен": ['Газонокосилки', 'Садовый инвентарь', 'Инструменты', 'Шкафы для одежды', 'Кровати', 'Шкафы-купе'],
    "H&M": ['Одежда', 'Обувь', 'Кроссовки', 'Пуховики', 'Рубашки', 'Платья'],
    "Zara": ['Одежда', 'Обувь', 'Кроссовки', 'Пуховики', 'Рубашки', 'Джинсы'],
    "Спортмастер": ['Спортивная одежда', 'Спортивный инвентарь', 'Велосипеды', 'Ролики', 'Палатки', 'Туристические рюкзаки', 'Кроссовки', 'Носки', 'Куртки']
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

def generate_datetime(open_time, close_time):
    open_dt = datetime.strptime(open_time, "%H:%M").replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
    close_dt = datetime.strptime(close_time, "%H:%M").replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
    
    random_time = open_dt + timedelta(minutes=random.randint(0, (close_dt - open_dt).seconds // 60))
    
    formatted_time = random_time.strftime("%Y-%m-%dT%H:%M:%S") + "+03:00"
    
    return formatted_time

def generate_card_number(bin_code, payment_system_code):
    remaining_digits = ''.join(random.choices('0123456789', k=10))
    return f"{payment_system_code}{bin_code}{remaining_digits}"

def generate_store_data(store, categories_and_brands, bank_probabilities, payment_system_probabilities, card_count):
    store_name, lat, lon, open_time, close_time = store
    coordinates = f"{lat:.8f}, {lon:.8f}"
    visit_time = generate_datetime(open_time, close_time)
    
    available_categories = store_categories.get(store_name.strip(), [])

    category = random.choice(available_categories)

    if category in categories_and_brands and categories_and_brands[category]:
        brand = random.choice(categories_and_brands[category][0])

    quantity = random.randint(5, 10) 

    base_price = categories_and_brands.get(category, (None, 0))[1]
    price = 0

    price_variation = base_price * random.uniform(-0.1, 0.1)
    price = max(round(base_price + price_variation), 1)
    total_price = price * quantity

    while True:
        bank = random.choices(list(bin_codes.keys()), weights=bank_probabilities)[0]
        bin_code = random.choice(bin_codes[bank])
        payment_system = random.choices(list(payment_systems.keys()), weights=payment_system_probabilities)[0]
        card_number = generate_card_number(bin_code, payment_systems[payment_system])

        if card_number in card_count:
            if card_count[card_number] < 5:
                card_count[card_number] += 1
                break
        else:
            card_count[card_number] = 1
            break

    return [store_name.strip(), visit_time, coordinates, category, brand, card_number, quantity, total_price]

def get_probabilities(probabilities_dict):
    while True:
        probabilities = []
        print("Введите вероятность для каждой платёжной системы (в сумме 100):")
        for system in probabilities_dict.keys():
            prob = float(input(f"{system}: "))
            probabilities.append(prob)

        if any(prob < 0 for prob in probabilities):
            print("Ошибка: вероятность не может быть отрицательной. Пожалуйста, введите значения снова.")
        elif sum(probabilities) != 100:
            print("Ошибка: суммы вероятностей должны равняться 100. Пожалуйста, введите значения снова.")
        else:
            return probabilities

payment_system_probabilities = get_probabilities(payment_systems)

bank_probabilities = get_probabilities(bin_codes)

while True:
    try:
        row_count = int(input("Введите количество строк для генерации (не менее 50000): "))
        if row_count < 50000:
            print("Ошибка: количество строк не должно быть меньше 50000.")
        else:
            break
    except ValueError:
        print("Ошибка: пожалуйста, введите целое число.")

dataset = []
card_count = {}
for _ in range(row_count):
    store = random.choice(stores)
    dataset.append(generate_store_data(store, categories_and_brands, bank_probabilities, payment_system_probabilities, card_count))

wb = Workbook()
ws = wb.active
ws.title = "Shopping Data"

headers = ['Название магазина', 'Дата и время', 'Координаты', 'Категория', 'Бренд', 'Номер карточки', 'Количество товаров', 'Стоимость']
ws.append(headers)

column_widths = [18, 27, 25, 25, 23, 18, 20, 11]
for i, width in enumerate(column_widths, 1):
    ws.column_dimensions[chr(64 + i)].width = width

for row in dataset:
    ws.append(row)

wb.save('shopping_dataset.xlsx')

print("Генерация завершена. Данные сохранены в файл 'shopping_dataset'.")
