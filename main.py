import csv
import re
import requests
import pprint

from pathlib import Path
from bs4 import BeautifulSoup


def get_site_access(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        src = response.text
        return BeautifulSoup(src, 'lxml')
    except Exception as ex:
        exit(f"{ex}\nCan't get data from server. URL: {url}")


def get_recipes_links(eda_url):
    soup = get_site_access(eda_url)

    dishes = soup.find_all(class_='horizontal-tile__item-title item-title')
    recipes_links = {}
    for dish in dishes:
        dish_title = re.sub(r'^\s+|\n|\r|\s+$', '', dish.find('span').text)
        dish_link = dish.find('a').get('href')
        recipes_links[re.sub(r'\xa0', ' ', dish_title)] = f'https://eda.ru{dish_link}'
    return recipes_links


def get_recipe(title, link):
    soup = get_site_access(link)
    # Записываем заголовки столбцов
    with open(f'recipes/{title}.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Ингредиенты',
                'Количество',
                'Цена'
            )
        )

    products = soup.find_all(class_='css-ipetvh-Column')
    # Перебираем продукты из списка ингредиентов
    for product in products:
        product_title = product.find(class_='css-12s4kyf-Info').find('span').text
        product_count = product.find(class_='css-1t5teuh-Info').text
        product_price = 0 # Здесь вызов функция с ценой

        with open(f'recipes/{title}.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    product_title,
                    product_count,
                    product_price
                )
            )
    # Создаем txt файл с инструкцией по приготовлению
    cooking_steps = soup.find_all(class_='css-18thmuh-Column')
    with open(f'recipes/{title}.txt', 'w') as file:
        for step in cooking_steps:
            file.write(f'{step.text}\n')


def main():
    Path('recipes').mkdir(parents=True, exist_ok=True)
    eda_url = 'https://eda.ru/recepty'
    recipes_links = get_recipes_links(eda_url)
    for dish_title, dish_link in recipes_links.items():
        get_recipe(dish_title, dish_link)


if __name__ == '__main__':
    main()
