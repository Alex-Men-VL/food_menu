import collections
import json
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def get_site_access(url):
    """Проверяет корректность ссылки возвращает объект класса BeautifulSoup."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        src = response.text
        return BeautifulSoup(src, 'lxml')
    except Exception as ex:
        exit(f"{ex}\nCan't get data from server. URL: {url}")


def get_recipes_links(eda_url):
    """Возвращает ссылки на блюда."""
    soup = get_site_access(eda_url)

    dishes = soup.find_all('div', class_='card__description')
    recipes_links = {}
    amount = 0  # Количество рецептов
    for dish in dishes:
        dish_title = dish.find('div', class_='card__title title').text
        dish_link = dish.find('a').get('href')
        recipes_links[dish_title] = f'https://www.edimdoma.ru{dish_link}'
        amount += 1
        if amount == 21:
            break
    return recipes_links


def get_recipe(title, link, meal):
    """Собирает информацию о блюде"""
    soup = get_site_access(link)

    # На сколько порций рассчитано
    portions = soup.find(class_='field__container').find(attrs={'name': 'servings'})['value']

    dish = collections.defaultdict(list)
    dish['Название блюда'] = title
    dish['Количество порций'] = portions
    fractions = ('½', '⅓', '¼', '⅕', '⅛')

    products = soup.find('div', {"id": "recipe_ingredients_block"}).find_all(class_='definition-list-table')
    # Перебираем продукты из списка ингредиентов
    for product in products:
        product_title = product.find(class_='recipe_ingredient_title').text
        dish['Ингредиенты'].append(product_title)

        product_count = product.find(class_='definition-list-table__td definition-list-table__td_value').text
        # Проверяем наличие цифр в product_count
        if re.search(r'\d+', product_count) or any(fraction for fraction in fractions if fraction in product_count):
            items = product_count.split()
            digit = [item for item in items if item.replace(',', '').isdigit() or item in fractions]
            measure = [item for item in items if item not in digit]
            dish['Количество'].append(''.join(digit))
            dish['Мера'].append(''.join(measure))
        else:
            dish['Количество'].append(None)
            dish['Мера'].append(product_count)
        product_price = 0  # Здесь вызов функция с ценой

    cooking_steps = soup.find_all(class_='plain-text recipe_step_text')
    # Записываем шаги готовки в словарь файл
    for number, step in enumerate(cooking_steps, 1):
        dish['Шаги готовки'].append(f'{number}. {step.text}')

    return dish


def get_recipes_by_category(meal, page_number):
    """Собирает данные по всем рецептам из данной категории и записывает их в JSON файл"""
    dishes = []
    edimdoma_url = f'https://www.edimdoma.ru/retsepty?page={page_number}&tags%5Brecipe_mealtime%5D%5B%5D={meal}'
    recipes_links = get_recipes_links(edimdoma_url)
    for dish_title, dish_link in recipes_links.items():
        dish = get_recipe(dish_title, dish_link, meal)
        dishes.append(dish)
    with open(f'recipes/{page_number}/{meal}.json', 'w', encoding='utf-8') as file:
        json.dump(dishes, file, indent=4, ensure_ascii=False)
    print(f'Обработка категории {meal} завершена.')
    return f'Обработка категории {meal} завершена.'


def main():
    if 'recipes' not in os.listdir('.'):
        Path('recipes').mkdir(parents=True, exist_ok=True)

        meals = ['завтрак', 'обед', 'ужин', 'полдник']
        # Скачиваем 5 различных списков блюд по каждому приему пищи
        for page in range(1, 6):
            Path(f'recipes/{page}').mkdir(parents=True, exist_ok=True)
            for meal in meals:
                get_recipes_by_category(meal, page)
        print('Списки рецептов успешно сформированы')
    else:
        print('Списки рецептов уже существуют')


if __name__ == '__main__':
    main()
