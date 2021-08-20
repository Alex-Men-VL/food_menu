import csv
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
    """Формирует csv файл с ингредиентами и txt файл с рецептом"""
    soup = get_site_access(link)
    Path(f'recipes/{meal}').mkdir(parents=True, exist_ok=True)
    # На сколько порций рассчитано
    portions = soup.find(class_='field__container').find(attrs={'name': 'servings'})['value']
    # Записываем заголовки столбцов
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

    products = soup.find('div', {"id": "recipe_ingredients_block"}).find_all(class_='definition-list-table')
    # Перебираем продукты из списка ингредиентов
    for product in products:
        product_title = product.find(class_='recipe_ingredient_title').text
        product_count = product.find(class_='definition-list-table__td definition-list-table__td_value').text
        product_price = 0  # Здесь вызов функция с ценой
        # Записываем ингредиент и его количество в таблицу csv
        with open(f'recipes/{meal}/{title}.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    product_title,
                    product_count,
                    product_price
                )
            )
    # Создаем txt файл с инструкцией по приготовлению
    cooking_steps = soup.find_all(class_='plain-text recipe_step_text')
    with open(f'recipes/{meal}/{title}.txt', 'w') as file:
        for number, step in enumerate(cooking_steps, 1):
            file.write(f'{number}. {step.text}\n\n')


def get_recipes_by_category(meals):
    for meal in meals:
        edimdoma_url = f'https://www.edimdoma.ru/retsepty?tags%5Brecipe_mealtime%5D%5B%5D={meal}&with_ingredient=&with_ingredient_condition=and&without_ingredient=&user_ids=&field=&direction=&query='
        recipes_links = get_recipes_links(edimdoma_url)
        for dish_title, dish_link in recipes_links.items():
            get_recipe(dish_title, dish_link, meal)
        print(f'Обработка категории {meal} завершена.')
    print('Все категории обработаны!')


def main():
    Path('recipes').mkdir(parents=True, exist_ok=True)
    meals = ['завтрак', 'обед', 'ужин']
    number_of_meals = int(input('Выберите количество приемов пищи в день (3 или 4): '))
    if number_of_meals == 4:
        meals.insert(2, 'полдник')
    get_recipes_by_category(meals)


if __name__ == '__main__':
    main()
