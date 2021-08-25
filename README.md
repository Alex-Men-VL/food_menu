# Рецепты блюд на неделю

Проект состоит из трех частей:

- `recipes.py` подготавливает списки рецептов с сайта
[edimdoma](https://www.edimdoma.ru/retsepty).
- `prices.py` составляет список цен на продукты с сайта [edadil](https://edadeal.ru/) и 
[ozon](https://www.ozon.ru/).
- `tg_bot.py` запускает телеграм бота.

## Возможности бота

- При первом запуске, после команды /start, вы получите приветственное сообщение, также станут
активны кнопки управления.
- Чтобы получить меню, необходимо нажать кнопку `Получить меню`. Таких кнопок две, различие - в
количестве приемов пищи в день (3 или 4).
- Вы также можете обновить список предлагаемых ботом блюд, нажав на `Обновить список рецептов`.
- После получения меню вы можете посмотреть подробное описание каждого дня, с указанием ингредиентов
и пошаговым рецептом готовки, нажав на кнопку `Подробное меню`.
- Также появится возможность получить список цен на продукты, нажав на `Цены на продукты`.
- Чтобы получить новое меню, нажмите на кнопку `Новое меню`.
- Если при работе с ботом у вас возникли какие-то проблемы, напиши `/help`.

## Запуск

- Скачать код;
- Перейти в виртуальное окружение;
- Установите Python пакеты из `requirements.txt`:
```bash
pip install -r requirements.txt
```
- Перед запуском бота, необходимо скачать списки рецептов:
```bash
python3 recipes.py
```
- После того как списки рецептов будут сформированы, нужно сформировать список цен на продукты:
  - Скачать актуальный [веб-драйвер](https://chromedriver.storage.googleapis.com/index.html) для браузера Google Chrome;
  - Разархивировать его;
  - Создайте файл .env;
  - Сохранить абсолютный путь к драйверу:
  ```bash
  PATH_TO_DRIVER=<абсолютный путь к драйверу>
  ```
  - Запустить скрипт для формирования списка цен на продукты:
  ```bash
  python3 prices.py
  ```
- Создайте создайте телеграм бота и запишите его токен в файл .env:
```bash
TG_TOKEN=<токен бота>
```
- Чтобы запустить бота, введите:
```bash
python3 tg_bot.py
```

### Важно

Не удалять созданную папку `recipes`, которая создаться при формировании
списка рецептов, иначе бот перестанет работать.