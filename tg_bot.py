import datetime
import json
import logging
import os
import random
import shutil
from pathlib import Path

from environs import Env
from telegram import Bot
from telegram.ext import CommandHandler, Updater


def start(update, context):
    user = update.effective_user
    name = user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Привет, {name}!\nЯ могу составить для тебя рацион питания на неделю.\n"
                                  "Напиши '/menu <количество приемов пищи в день (3/4)>' для получения рациона.")


def make_folder(current_date):
    last_date = current_date + datetime.timedelta(days=6)

    folder_name = f'Подробное меню на {current_date.strftime("%d-%b-%Y")} - {last_date.strftime("%d-%b-%Y")}'

    if folder_name in os.listdir('.'):
        shutil.rmtree(folder_name)
    Path(folder_name).mkdir(exist_ok=True)
    return folder_name


def menu(update, context):
    meals = ['завтрак', 'обед', 'ужин', 'полдник']
    if '4' in context.args:
        meals[-1], meals[-2] = meals[-2], meals[-1]
        meals_count = 4
    else:
        meals_count = 3

    used = []
    current_date = datetime.datetime.now()
    folder_name = make_folder(current_date)

    for day in range(1, 8):
        # Создаем txt файл с меню на первый день
        total_date = current_date + datetime.timedelta(days=day - 1)
        file = open(f'{folder_name}/{total_date.strftime("%d-%b-%Y")}.txt', 'a')

        bot_text = f'{total_date.strftime("%d-%b-%Y")}\n'

        for meal in meals[0:meals_count]:
            # Сохраняем список блюд для конкретного приема пищи
            with open(f'recipes/{meal}.json', 'r') as file_json:
                recipes = json.load(file_json)

            # Находим рецепт, который еще не выводился
            while True:
                dish = random.choice(recipes)
                if dish['id'] not in used:
                    used.append(dish['id'])
                    break

            file.write(f'\n***{meal.title()}***\n')
            bot_text += f'***{meal.title()}***\n'

            file.write(f'Название блюда: {dish["Название блюда"]}\n')
            bot_text += f'Название блюда: {dish["Название блюда"]}\n'

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

            used.append(dish['id'])

        file.close()
        context.bot.send_message(chat_id=update.effective_chat.id, text=bot_text)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(f'{folder_name}/{total_date.strftime("%d-%b-%Y")}.txt'))


def post_menu_in_tg():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    env = Env()
    env.read_env()

    tg_token = env('TG_TOKEN')
    bot = Bot(token=tg_token)
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    make_menu = CommandHandler('menu', menu)
    dispatcher.add_handler(make_menu)

    updater.start_polling()
    updater.idle()
