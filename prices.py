import json
import os

from environs import Env
from selenium import webdriver
import logging
import time
from bs4 import BeautifulSoup


def get_data(url, path):
    """Сохраняет html код страницы с ценами"""
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
    ]

    options = webdriver.ChromeOptions()
    options.add_argument(
        f'user-agent={user_agents}'
    )

    try:
        driver = webdriver.Chrome(
            executable_path=path,
            options=options
        )
        driver.get(url=url)
        time.sleep(2)

        with open('index.html', 'w') as file:
            file.write(driver.page_source)

    except Exception as ex:
        logging.error(ex)
    finally:
        driver.close()
        driver.quit()


def get_edadil_price(url, path):
    """Определяет цену продукта с сайта edadil"""
    get_data(url, path)
    with open('index.html') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    samples = soup.find_all('div', class_='b-offer__quantity')
    prices_per_unit = []
    count = 0
    for sample in samples:
        price_per_unit = tuple((sample.text.split('/')[-1]).replace(',', '.').split())
        prices_per_unit.append(price_per_unit)
        count += 1
        if count == 6:
            break
    prices_per_unit.sort(key=lambda price: float(price[0]))
    if len(prices_per_unit) > 1:
        average_price_per_unit = prices_per_unit[len(prices_per_unit) // 2]
    elif len(prices_per_unit) == 1:
        average_price_per_unit = prices_per_unit[0]
    else:
        average_price_per_unit = None
    return average_price_per_unit


def get_yandex_price(url, path):
    """Определяет цену продукта с сайта Яндекс Маркет"""
    get_data(url, path)
    with open('index.html') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    samples = soup.find_all('div', class_='e3f7')
    prices_per_unit = []
    count = 0
    for sample in samples:
        name = sample.find('span', {'class': 'j4 as3 az a0f2 f-tsBodyL item e3t0'}).find('span').get_text()
        name_text = name.split()
        digit, measure = None, None
        for number, word in enumerate(name_text):
            if word.isdigit():
                digit = word
                measure = name_text[number + 1]
                break
        unit = ["за", digit, measure]
        # unit.insert("за")
        price = sample.find('div', class_='_24d4').find('span').text.split()
        if unit and price:
            prices_per_unit.append((*price, *unit))

        count += 1
        if count == 6:
            break

    prices_per_unit.sort(key=lambda price: float(price[0]))
    if len(prices_per_unit) > 1:
        average_price_per_unit = prices_per_unit[(len(prices_per_unit) // 2) - 1]
    elif len(prices_per_unit) == 1:
        average_price_per_unit = prices_per_unit[0]
    else:
        average_price_per_unit = None
    print(average_price_per_unit)
    return average_price_per_unit


def make_products_list_with_prices(folder_name, prices_for_products, path):
    """Перебирает все ингредиенты и сохраняет их цену в список"""
    meals = ['завтрак', 'обед', 'ужин', 'полдник']
    for meal in meals:
        with open(f'recipes/{folder_name}/{meal}.json', 'r') as file_json:
            recipes = json.load(file_json)
        for recipe in recipes:
            products = recipe['Ингредиенты']
            for product in products:
                if product not in prices_for_products:
                    edadil_url = f'https://edadeal.ru/sankt-peterburg/offers?search={product}&title={product}'
                    prices_for_products[product] = get_edadil_price(edadil_url, path)


def main():
    env = Env()
    env.read_env()
    path = env('PATH_TO_DRIVER')
    prices_for_products = {}
    # Если списка цен нет, то парсим сайт edadil
    if 'prices.json' not in os.listdir('recipes'):
        for folder in os.listdir('recipes'):
            if '.' not in folder:
                make_products_list_with_prices(folder, prices_for_products, path)

        with open('recipes/prices_not_full.json', 'w', encoding='utf-8') as file_json:
            json.dump(prices_for_products, file_json, indent=4, ensure_ascii=False)

        # Парсим сайт Яндекс Маркет, чтобы получить цены на не найденный на первом сайте продукты
        with open('recipes/prices_not_full.json') as file_json:
            products = json.load(file_json)

        for product in products.keys():
            if not products[product]:
                ozon_url = f'https://www.ozon.ru/category/produkty-pitaniya-9200/?from_global=true&text={product}'
                print(product)
                products[product] = get_yandex_price(ozon_url, path)

        with open('recipes/prices2.json', 'w') as file_json:
            json.dump(products, file_json, indent=4, ensure_ascii=False)
        print('Список цен на продукты успешно сформирован')
    else:
        print('Список цен на продукты уже существует')


if __name__ == '__main__':
    main()
