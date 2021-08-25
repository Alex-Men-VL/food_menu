import datetime
import json
import os
import random
import shutil
from pathlib import Path

import telebot
from environs import Env
from telebot import types

env = Env()
env.read_env()
token = env('TG_TOKEN')

bot = telebot.TeleBot(token)

# При первом запуске бота, рецепты берутся из папки recipes/1
page_number = 1


@bot.message_handler(commands=['start'])
def start_message(message):
    Path('Users').mkdir(parents=True, exist_ok=True)
    user = message.from_user
    name = user.first_name
    bot_name = bot.get_me().first_name

    # Кнопки на основном экране для получения рационов питания
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_button_3 = types.KeyboardButton("Получить меню с тремя приемами пищи")
    menu_button_4 = types.KeyboardButton("Получить меню с четырьмя приемами пищи")
    menu_button_load = types.KeyboardButton("Обновить список рецептов")
    markup.row(menu_button_3, menu_button_4)
    markup.row(menu_button_load)

    # Приветствие бота
    bot.send_message(message.chat.id, f'Добро пожаловать, {name}! Я - {bot_name}.\n'
                                      f'Я могу составить для вас меню на неделю.\n\n'
                                      f'_Нажмите на кнопку_ *Получить меню*_, выбрав количество приемов пищи_.\n'
                                      f'_Если вы хотите узнать о всех моих возможностях, введите /help_.',
                     reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def get_help(message):
    """Отправляет сообщение, описывающее все возможности бота"""
    bot.send_message(message.chat.id,
                     '1) Чтобы получить меню на неделю, нажмите на одну из верхних кнопок внизу экрана, '
                     'в зависимости от того, сколько приемов пищи в день вы предпочитаете.\n'
                     '2) Получив меню, вы можете нажать на *Подробное меню*, при этом вы получите ответное сообщение,'
                     'в котором сможете выбрать день, подробное меню которого хотите получить в виде txt файла.\n'
                     '3) Чтобы получить список цен на продукты из меню, нажмите на *Цены на продукты*.'
                     '4) Чтобы получить новое меню, нажмите на *Новое меню*.\n'
                     '5) Если вам не нравятся те блюда, которые предлагает бот, нажмите на кнопку *Новое меню*,'
                     'a затем на *Обновить список рецептов*',
                     parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def post_menu(message):
    """Отправляет краткое меню на неделю с 3/4 приемами пищи в день"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_button_detail = types.KeyboardButton("Подробное меню")
    menu_button_price = types.KeyboardButton("Цены на продукты")
    menu_button_new_menu = types.KeyboardButton("Новое меню")
    markup.row(menu_button_detail, menu_button_price)
    markup.row(menu_button_new_menu)

    if message.text == 'Получить меню с тремя приемами пищи':
        bot_text = make_menu(message, 3)
        bot.send_message(message.chat.id, bot_text, parse_mode='Markdown', reply_markup=markup)
        bot.send_message(message.chat.id, '_Если у вас возникли проблемы, введите /help_', parse_mode='Markdown')
    elif message.text == 'Получить меню с четырьмя приемами пищи':
        bot_text = make_menu(message, 4)
        bot.send_message(message.chat.id, bot_text, parse_mode='Markdown', reply_markup=markup)
        bot.send_message(message.chat.id, '_Если у вас возникли проблемы, введите /help_', parse_mode='Markdown')
    elif message.text == 'Обновить список рецептов':
        load_recipes(message)
    elif message.text == 'Подробное меню':
        post_recipes(message)
    elif message.text == 'Цены на продукты':
        file = open(f'Users/ID_{message.from_user.id}/цены.txt', 'r')
        bot.send_document(message.chat.id, file)
    elif message.text == 'Новое меню':
        choose_menu(message)


def choose_menu(message):
    """Функция выводит кнопки для составления меню """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_button_3 = types.KeyboardButton("Получить меню с тремя приемами пищи")
    menu_button_4 = types.KeyboardButton("Получить меню с четырьмя приемами пищи")
    menu_button_load = types.KeyboardButton("Обновить список рецептов")
    markup.row(menu_button_3, menu_button_4)
    markup.row(menu_button_load)
    bot.send_message(message.chat.id, f'_Нажмите на кнопку_ *Получить меню*_,с нужным количеством приемов пищи_.\n',
                     reply_markup=markup, parse_mode='Markdown')


def load_recipes(message):
    """Обновляет папку со списками рецептов"""
    global page_number

    page_number += 1
    if page_number == 6:
        page_number = 1

    bot.send_message(message.chat.id, 'Список рецептов обновлен!')


def post_recipes(message):
    """Отправляет сообщение с кнопками, нажав на которые можно получить подробное описание меню на каждый день"""
    current_date = datetime.datetime.now()
    markup = types.InlineKeyboardMarkup()
    for day in range(7):
        total_date = current_date + datetime.timedelta(days=day)
        markup.add(types.InlineKeyboardButton(f'Меню на {total_date.strftime("%d-%b-%Y")}', callback_data=str(day)))

    bot.send_message(message.chat.id, 'На какой день вам показать меню?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """Отправляет txt файл с подробным меню"""
    if call.data.isdigit():
        current_date = datetime.datetime.now()
        folder_name = f'ID_{call.message.chat.id}'
        if folder_name in os.listdir('Users'):
            total_date = current_date + datetime.timedelta(days=int(call.data))
            file = open(f'Users/{folder_name}/{total_date.strftime("%d-%b-%Y")}.txt', 'r')
            bot.send_document(call.message.chat.id, file)

        # Удаляем сообщение с кнопками
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Подробное меню',
                              reply_markup=None)

        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                  text='Если вы не получили файл с подробным меню, '
                                       'нажмите на кнопку "Получить меню"')


def make_menu(message, meals_count):
    """Составляет меню на неделю"""
    meals = ['завтрак', 'обед', 'ужин', 'полдник']
    if meals_count == 4:
        meals[-1], meals[-2] = meals[-2], meals[-1]

    used = []
    current_date = datetime.datetime.now()

    folder_name = f'ID_{message.from_user.id}'

    if folder_name in os.listdir('Users'):
        shutil.rmtree(f'Users/{folder_name}')
    Path(f'Users/{folder_name}').mkdir(parents=True, exist_ok=True)

    bot_text = ''
    products = set()

    for day in range(1, 8):
        # Создаем txt файл с меню на первый день
        total_date = current_date + datetime.timedelta(days=day - 1)
        file = open(f'Users/{folder_name}/{total_date.strftime("%d-%b-%Y")}.txt', 'a')

        bot_text += f'*{total_date.strftime("%d-%b-%Y")}*\n\n'

        for meal in meals[0:meals_count]:
            # Сохраняем список блюд для конкретного приема пищи
            with open(f'recipes/{page_number}/{meal}.json', 'r') as file_json:
                recipes = json.load(file_json)

            # Находим рецепт, который еще не выводился
            while True:
                dish = random.choice(recipes)
                if dish['id'] not in used:
                    used.append(dish['id'])
                    break

            file.write(f'\n{meal.title()}: {dish["Название блюда"]}\n')
            bot_text += f'*{meal.title()}*: {dish["Название блюда"]}\n'

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
        bot_text += '\n'
        file.close()

    # Создаем файл с ценами на продукты
    with open('recipes/prices.json') as file_json:
        prices = json.load(file_json)
    file = open(f'Users/{folder_name}/цены.txt', 'a')

    for product in products:
        if product in prices:
            product_price = " ".join(prices[product])
            file.write(f'{product}: {product_price}\n')
    file.close()

    return bot_text


bot.polling()
