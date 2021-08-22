import datetime
import json
import os
import random
import shutil
from pathlib import Path

from recipes import get_recipes_by_category
from tg_bot import post_menu_in_tg


def make_menu_for_week(meals, meals_count, used):
    """Выводит подробное меню каждого приема пищи для первого дня.
    Создает txt файл в папке 'Подробные рецепты' с аналогичной информацией.
    """
    if meals_count == 4:
        meals[-1], meals[-2] = meals[-2], meals[-1]

    current_date = datetime.datetime.now()
    last_date = current_date + datetime.timedelta(days=6)

    folder_name = f'Подробное меню на {current_date.strftime("%d-%b-%Y")} - {last_date.strftime("%d-%b-%Y")}'

    if folder_name in os.listdir('.'):
        shutil.rmtree(folder_name)
    Path(folder_name).mkdir(exist_ok=True)

    # Создаем txt файл с меню на первый день
    file = open(f'{folder_name}/{current_date.strftime("%d-%b-%Y")}.txt', 'a')

    print('\t\u001b[31;1mДень № 1', f"({current_date.strftime('%d-%b-%Y')})\u001b[0m")

    for meal in meals[0:meals_count]:
        # Сохраняем список блюд для конкретного приема пищи
        with open(f'recipes/{meal}.json', 'r') as file_json:
            recipes = json.load(file_json)

        random.shuffle(recipes)
        dish = recipes[0]

        print(f'\u001b[32;1m***{meal.title()}***\u001b[0m')
        file.write(f'***{meal.title()}***\n')

        print('\u001b[33;1mНазвание блюда:\u001b[0m', dish['Название блюда'])
        file.write(f'Название блюда: {dish["Название блюда"]}\n')

        print('\n\u001b[33;1mИнгредиенты:\u001b[0m')
        file.write('\nИнгредиенты:\n')

        for number, product in enumerate(dish['Ингредиенты']):
            if dish['Количество'][number]:
                print(product, ':', dish['Количество'][number], dish['Мера'][number])
                file.write(f'{product} : {dish["Количество"][number]} {dish["Мера"][number]}\n')
            else:
                print(product, ':', dish['Мера'][number])
                file.write(f'{product} : {dish["Мера"][number]}\n')

        print('\n\u001b[33;1mПОШАГОВЫЙ РЕЦЕПТ:\u001b[0m')
        file.write('\nПОШАГОВЫЙ РЕЦЕПТ:\n')

        for step in dish['Шаги готовки']:
            print(step)
            file.write(f'{step}\n')
        print()
        file.write('\n')

        used.append(dish['id'])

    file.close()
    # Вызываем функцию для вывода меню на остальные 6 дней.
    make_menu_other_days(meals[0:meals_count], used, current_date, folder_name)


def make_menu_other_days(meals, used, current_date, folder_name):
    """Функция выводит краткое меню на остальные 6 дней.
    Создает txt файл в папке 'Подробные рецепты' с подробными рецептами.
    """
    for day_number in range(2, 8):
        next_date = current_date + datetime.timedelta(days=day_number-1)

        file = open(f'{folder_name}/{next_date.strftime("%d-%b-%Y")}.txt', 'a')

        print(f'\t\u001b[31;1m День № {day_number}', f"({next_date.strftime('%d-%b-%Y')})\u001b[0m")

        for meal in meals:
            print(f'\u001b[32;1m***{meal.title()}***\u001b[0m')
            file.write(f'***{meal.title()}***\n')
            # Сохраняем список блюд для конкретного приема пищи
            with open(f'recipes/{meal}.json', 'r') as file_json:
                recipes = json.load(file_json)
            # Находим рецепт, который еще не выводился
            while True:
                dish = random.choice(recipes)
                if dish['id'] not in used:
                    used.append(dish['id'])
                    break

            file.write(f'Название блюда: {dish["Название блюда"]}\n')
            print(dish['Название блюда'], '\n')

            file.write('\nИнгредиенты:\n')
            for number, product in enumerate(dish['Ингредиенты']):
                if dish['Количество'][number]:
                    file.write(f'{product} : {dish["Количество"][number]} {dish["Мера"][number]}\n')
                else:
                    file.write(f'{product} : {dish["Мера"][number]}\n')

            file.write('\nПОШАГОВЫЙ РЕЦЕПТ:\n')
            for step in dish['Шаги готовки']:
                file.write(f'{step}\n')
            file.write('\n')
        file.close()


def download_recipes(meals):
    """Загружает рецепты блюд для каждого приема пищи."""
    flag = False
    # Проверяем наличие списка блюд для каждого приема пищи
    for meal in meals:
        if f'{meal}.json' not in os.listdir('recipes'):
            get_recipes_by_category(meal)
            flag = True
    if flag:
        print('Все категории обработаны!\n')


def output_to_console(meals):
    """Функция выводит меню в консоль."""
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


def main():
    Path('recipes').mkdir(parents=True, exist_ok=True)
    meals = ['завтрак', 'обед', 'ужин', 'полдник']
    # Загружаем рецепты каждого приема пищи
    download_recipes(meals)
    # Выводим меню в консоль
    # output_to_console(meals)
    # Выводим в тг через бота
    post_menu_in_tg()


if __name__ == '__main__':
    main()
