import datetime
import json
import os
import random
from pathlib import Path

from recipes import get_recipes_by_category


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



if __name__ == '__main__':
    main()
