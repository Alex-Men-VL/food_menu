# Рецепты блюд на неделю

Скрипт скачивает рецепты блюд четырех категорий: завтрак, обед, полдник и ужин. Все данные по каждой категории сохраняются в 
отдельные json файлы в папку recipes. 

Основная работа скрипта происходит в Telegram через бота.

## Запуск

- Скачать код;
- Перейти в виртуальное окружение;
- Установите Python пакеты из `requirements.txt`:
```bash
pip install -r requirements.txt
```
- Создайте файл .env и добавьте в него токен бота:
```bash
TG_TOKEN = <токен бота>
```
- Чтобы запустить бота, введите:
```bash
python3 tg_bot.py
```
