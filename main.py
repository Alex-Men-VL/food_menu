import datetime
import json
import os
import random
from pathlib import Path

from recipes import get_recipes_by_category


def make_menu_for_week(meals, meals_count, used):
    """Выводит подробное меню каждого приема пищи для первого дня."""
    if meals_count == 4:
        meals[-1], meals[-2] = meals[-2], meals[-1]

    current_date = datetime.datetime.now()
    print('\t\u001b[31;1mДень № 1', f"({current_date.strftime('%d-%b-%Y')})\u001b[0m")

    for meal in meals[0:meals_count]:
        # Сохраняем список блюд для конкретного приема пищи
        with open(f'recipes/{meal}.json', 'r') as file:
            recipes = json.load(file)
        random.shuffle(recipes)
        dish = recipes[0]
        print(f'\u001b[32;1m***{meal.title()}***\u001b[0m')

        print('\u001b[33;1mНазвание блюда:\u001b[0m', dish['Название блюда'])

        print('\n\u001b[33;1mИнгредиенты:\u001b[0m')
        for number, product in enumerate(dish['Ингредиенты']):
            if dish['Количество'][number]:
                print(product, ':', dish['Количество'][number], dish['Мера'][number])
            else:
                print(product, ':', dish['Мера'][number])

        print('\n\u001b[33;1mПОШАГОВЫЙ РЕЦЕПТ:\u001b[0m')
        for step in dish['Шаги готовки']:
            print(step)
        print()
        used.append(dish['id'])
    # Вызываем функцию для вывода меню на остальные 6 дней.
    make_menu_other_days(meals[0:meals_count], used, current_date)


def make_menu_other_days(meals, used, current_date):
    """Функция выводит краткое меню на остальные 6 дней."""
    for day_number in range(2, 8):
        next_date = current_date + datetime.timedelta(days=day_number)
        print(f'\t\u001b[31;1m День № {day_number}', f"({next_date.strftime('%d-%b-%Y')})\u001b[0m")

        for meal in meals:
            print(f'\u001b[32;1m***{meal.title()}***\u001b[0m')
            # Сохраняем список блюд для конкретного приема пищи
            with open(f'recipes/{meal}.json', 'r') as file:
                recipes = json.load(file)
            # Находим рецепт, который еще не выводился
            while True:
                dish = random.choice(recipes)
                if dish['id'] not in used:
                    used.append(dish['id'])
                    break
            print(dish['Название блюда'], '\n')


def main():
    Path('recipes').mkdir(parents=True, exist_ok=True)
    meals = ['завтрак', 'обед', 'ужин', 'полдник']
    flag = False
    # Проверяем наличие списка блюд для каждого приема пищи
    for meal in meals:
        if f'{meal}.json' not in os.listdir('recipes'):
            get_recipes_by_category(meal)
            flag = True
    if flag:
        print('Все категории обработаны!\n')

    print('Привет!')
    while True:
        message_1 = input("Напиши \u001b[32;1mхочу меню\u001b[0m, чтобы получить меню на неделю.\n")
        if message_1 == 'хочу меню':
            meals_count = int(input('Сколько приемов пищи в день ты хочешь (3/4)?\n'))
            used = []
            make_menu_for_week(meals, meals_count, used)
            break
        else:
            print('Я тебя не понял.')


if __name__ == '__main__':
    main()
