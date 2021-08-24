import collections
import csv
import json
import re

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


def make_csv_with_headers(meal, title, portions):
    """Формирует csv файл с заголовками столбцов и информацией о количестве порций."""
    with open(f'recipes/{meal}/{title}.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Ингредиенты',
                'Количество',
                'Цена',
                f'Количество порций: {portions}'
            )
        )


def add_to_csv(meal, title, product_info):
    """Записывает ингредиенты в csv файл."""
    with open(f'recipes/{meal}/{title}.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                product_info[0],
                product_info[1],
                product_info[2]
            )
        )


def make_txt_with_cooking_steps(cooking_steps, meal, title):
    with open(f'recipes/{meal}/{title}.txt', 'w') as file:
        for number, step in enumerate(cooking_steps, 1):
            file.write(f'{number}. {step.text}\n\n')


count = 0


def get_recipe(title, link, meal, count):
    """Собирает информацию о блюде"""
    soup = get_site_access(link)
    # Path(f'recipes/{meal}').mkdir(parents=True, exist_ok=True)
    # На сколько порций рассчитано
    portions = soup.find(class_='field__container').find(attrs={'name': 'servings'})['value']

    # Записываем заголовки столбцов
    # make_csv_with_headers(meal, title, portions)

    dish = collections.defaultdict(list)
    dish['Название блюда'] = title
    dish['Количество порций'] = portions
    dish['id'] = count
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
        product_info = [product_title, product_count, product_price]
        # Записываем ингредиенты в csv файл
        # add_to_csv(meal, title, product_info)

    cooking_steps = soup.find_all(class_='plain-text recipe_step_text')
    # Записываем шаги готовки в словарь файл
    for number, step in enumerate(cooking_steps, 1):
        dish['Шаги готовки'].append(f'{number}. {step.text}')

    return dish
    # Создаем txt файл с инструкцией по приготовлению
    # make_txt_with_cooking_steps(cooking_steps, meal, title)

    # Записываем информацию о блюде в json файл
    # with open(f'recipes/{meal}.json', 'a', encoding='utf-8') as file:
    #     json.dump(dish, file, indent=4, ensure_ascii=False)


def get_recipes_by_category(meal, page_number):
    """Собирает данные по всем рецептам из данной категории и записывает их в JSON файл"""
    global count

    dishes = []
    # edimdoma_url = f'https://www.edimdoma.ru/retsepty?tags%5Brecipe_mealtime%5D%5B%5D={meal}&with_ingredient=&with_ingredient_condition=and&without_ingredient=&user_ids=&field=&direction=&query='
    edimdoma_url = f'https://www.edimdoma.ru/retsepty?page={page_number}&tags%5Brecipe_mealtime%5D%5B%5D={meal}'
    recipes_links = get_recipes_links(edimdoma_url)
    for dish_title, dish_link in recipes_links.items():
        dish = get_recipe(dish_title, dish_link, meal, count)
        dishes.append(dish)
        count += 1
    with open(f'recipes/{meal}.json', 'w', encoding='utf-8') as file:
        json.dump(dishes, file, indent=4, ensure_ascii=False)
    print(f'Обработка категории {meal} завершена.')
    return f'Обработка категории {meal} завершена.'
