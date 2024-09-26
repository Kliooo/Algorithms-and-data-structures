import random
from datetime import datetime, timedelta
from openpyxl import Workbook

# Функция для чтения данных из файла
def load_data_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

# Данные по BIN-кодам банков
bin_codes = {
    "Сбербанк": ["27402", "27406", "27411", "27416", "27417", "27418", "27420", "27422", "27425", "27427"],
    "ВТБ": ["18868", "18869", "18870", "18873", "21191", "26375", "30127", "31723", "40622", "40623"],
    "ПСБ": ["02507", "04906", "24561", "24562", "24563", "26803", "26804", "29726", "29727", "29728"],
    "Газпромбанк": ["04136", "04270", "04271", "04272", "04273", "24974", "24975", "24976", "26890", "27326"],
    "Альфа-Банк": ["10584", "15400", "15428", "15429", "15481", "15482", "19539", "19540", "21118", "27714"],
}

# Данные по платежным системам
payment_systems = {
    "МИР": "2",
    "Visa": "4",
    "MasterCard": "5",
}

# Функция для генерации номера карты
def generate_card_number(bin_code, payment_system_code):
    remaining_digits = ''.join(random.choices('0123456789', k=10))
    return f"{payment_system_code}{bin_code}{remaining_digits}"

# Загрузка списка магазинов и их координат из файла store_coordinates.txt
stores = load_data_from_file('Laboratory_1/store_coordinates.txt')

# Загрузка брендов по категориям из файла brands.txt
categories_and_brands = {}
with open('Laboratory_1/brands.txt', 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if ':' in line:
            parts = line.split(':')
            category = parts[0].strip()
            brands_and_price = parts[1].rsplit(';', 1)  # Разделяем по последнему ;
            brands_list = [brand.strip() for brand in brands_and_price[0].split(';')]
            average_price = float(brands_and_price[1].strip())  # Средняя стоимость
            categories_and_brands[category] = (brands_list, average_price)  # Сохраняем и стоимость

# Определение категорий для каждого магазина
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
    "OBI": ['Газонокосилки', 'Садовый инвентарь', 'Инструменты', 'Стройматериалы', 'Шкафы для одежды', 'Комоды', 'Кровати', 'Игровые столы', 'Камеры видеонаблюдения'],
    "Леруа Мерлен": ['Газонокосилки', 'Садовый инвентарь', 'Инструменты', 'Стройматериалы', 'Шкафы для одежды', 'Кровати', 'Шкафы-купе'],
    "H&M": ['Одежда', 'Обувь', 'Кроссовки', 'Пуховики', 'Рубашки', 'Платья'],
    "Zara": ['Одежда', 'Обувь', 'Кроссовки', 'Пуховики', 'Рубашки', 'Джинсы'],
    "Спортмастер": ['Спортивная одежда', 'Спортивный инвентарь', 'Велосипеды', 'Ролики', 'Палатки', 'Туристические рюкзаки', 'Кроссовки', 'Носки', 'Куртки']
}

# Функция для генерации случайной даты и времени посещения магазина
def generate_random_datetime():
    start_time = datetime.strptime("2024-01-22T10:00+03:00", "%Y-%m-%dT%H:%M%z")
    end_time = datetime.strptime("2024-01-22T22:00+03:00", "%Y-%m-%dT%H:%M%z")
    random_time = start_time + timedelta(minutes=random.randint(0, (end_time - start_time).seconds // 60))
    
    # Форматирование времени с двоеточием в смещении
    formatted_time = random_time.strftime("%Y-%m-%dT%H:%M:%S") + random_time.strftime("%z")[:3] + ":" + random_time.strftime("%z")[3:]
    
    return formatted_time



# Функция для генерации строки данных для одного магазина
# Функция для генерации строки данных для одного магазина
def generate_store_data(store, categories_and_brands, bank_probabilities, payment_system_probabilities, card_count):
    store_name, lat, lon = store.split(',')
    coordinates = f"{float(lat.strip()):.8f}, {float(lon.strip()):.8f}"
    visit_time = generate_random_datetime()
    
    # Определение категорий, доступных для данного магазина
    available_categories = store_categories.get(store_name.strip(), [])

    if not available_categories:
        return [store_name.strip(), visit_time, coordinates, "Неизвестно", "Неизвестно", "Неизвестно", 0, 0]

    # Выбор категории
    category = random.choice(available_categories)

    # Проверка наличия брендов для категории
    if category in categories_and_brands and categories_and_brands[category]:
        brand = random.choice(categories_and_brands[category][0])  # Исправлено: выбор бренда из списка
    else:
        brand = "Неизвестно"

    # Генерация количества товаров (минимум 5)
    quantity = random.randint(5, 10)

    # Определение средней цены для категории
    base_price = categories_and_brands.get(category, (None, 0))[1]
    price = 0  # Инициализация переменной price

    if base_price > 0:
        # Генерация цены с учетом ±10% от средней
        price_variation = base_price * random.uniform(-0.1, 0.1)
        price = max(round(base_price + price_variation), 1)  # Генерация цены для одного товара

    total_price = price * quantity  # Общая стоимость за количество товаров

    # Генерация номера карты
    while True:
        bank = random.choices(list(bin_codes.keys()), weights=bank_probabilities)[0]
        bin_code = random.choice(bin_codes[bank])
        payment_system = random.choices(list(payment_systems.keys()), weights=payment_system_probabilities)[0]
        card_number = generate_card_number(bin_code, payment_systems[payment_system])

        # Проверка количества повторов номера карты
        if card_number in card_count:
            if card_count[card_number] < 5:
                card_count[card_number] += 1
                break
        else:
            card_count[card_number] = 1
            break

    return [store_name.strip(), visit_time, coordinates, category, brand, card_number, quantity, total_price]

# Функция для получения вероятностей
def get_probabilities(probabilities_dict):
    while True:
        probabilities = []
        print("Введите вероятность для каждой платёжной системы (в сумме 100):")
        for system in probabilities_dict.keys():
            prob = float(input(f"{system}: "))
            probabilities.append(prob)

        # Проверка на отрицательные значения и сумму
        if any(prob < 0 for prob in probabilities):
            print("Ошибка: вероятность не может быть отрицательной. Пожалуйста, введите значения снова.")
        elif sum(probabilities) != 100:
            print("Ошибка: суммы вероятностей должны равняться 100. Пожалуйста, введите значения снова.")
        else:
            return probabilities

# Ввод вероятностей для платежной системы
payment_system_probabilities = get_probabilities(payment_systems)

# Ввод вероятностей для банков
bank_probabilities = get_probabilities(bin_codes)

# Запрос количества строк для генерации
while True:
    try:
        row_count = int(input("Введите количество строк для генерации (не менее 50000): "))
        if row_count < 50000:
            print("Ошибка: количество строк не должно быть меньше 50000.")
        else:
            break
    except ValueError:
        print("Ошибка: пожалуйста, введите целое число.")

# Генерация данных для заданного количества строк
dataset = []
card_count = {}  # Словарь для отслеживания количества повторов карт
for _ in range(row_count):
    store = random.choice(stores)
    dataset.append(generate_store_data(store, categories_and_brands, bank_probabilities, payment_system_probabilities, card_count))

# Создание Excel файла
wb = Workbook()
ws = wb.active
ws.title = "Shopping Data"

# Заголовки столбцов
headers = ['Название магазина', 'Дата и время', 'Координаты', 'Категория', 'Бренд', 'Номер карточки', 'Количество товаров', 'Стоимость']
ws.append(headers)

# Установка ширины столбцов
column_widths = [18, 27, 25, 25, 23, 18, 20, 11]  # Ширина для каждого столбца
for i, width in enumerate(column_widths, 1):  # i начинается с 1, так как столбцы нумеруются с 1
    ws.column_dimensions[chr(64 + i)].width = width  # chr(64 + i) даёт букву столбца

# Добавление данных в Excel
for row in dataset:
    ws.append(row)

# Сохранение Excel файла
wb.save('shopping_dataset.xlsx')

print("Генерация завершена. Данные сохранены в файл 'shopping_dataset.xlsx'.")
