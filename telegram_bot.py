from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from connection_to_db import Database
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage


def get_token(raised=False):
    try:
        if raised:
            print('ну вот')
            raise Exception
        file = open('token.txt', 'rb')
        TOKEN = file.readline().decode()
        file.close()
    except:
        file = open('token.txt', 'wb')
        TOKEN = input('Введите токен бота: ')
        to_save = input('Сохранить пароль? (Д/Н): ').lower()
        if to_save in 'дy':
            file.write(TOKEN.encode())
            file.close()
        else:
            file.close()
    return TOKEN


while True:
    try:
        TOKEN = get_token(False)
        break
    except Exception as ex:
        TOKEN = get_token(True)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

while True:
    try:
        db = Database()
        db.connect_to_db()
        break
    except Exception as ex:
        print(ex)

db.cursor.execute("SELECT name FROM category")
categories = [elem[0] for elem in db.cursor.fetchall()]
category_buttons = [types.InlineKeyboardButton(text=elem, callback_data=elem) for elem in categories]

db.cursor.execute("SELECT DISTINCT(difficulty) FROM task")
difficulties = [str(elem[0]) for elem in db.cursor.fetchall()]
difficulty_buttons = [types.InlineKeyboardButton(text=elem, callback_data=elem) for elem in difficulties]


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('/set_contest', '/clear_all_contests')
    await message.answer("Привет! Это составитель контестов.", reply_markup=keyboard)


@dp.message_handler(Command("set_contest"))
async def cmd_set_contest(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*category_buttons)
    await message.answer("Выберите категорию:", reply_markup=keyboard)


@dp.message_handler(Command("clear_all_contests"))
async def cmd_clear_all_contests(message: types.Message):
    db.cursor.execute("UPDATE task SET is_in_contest=FALSE")


@dp.callback_query_handler(lambda c: c.data in difficulties)
async def select_tasks(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        category = data['category']
    db.cursor.execute(f"""
    SELECT task.id, title, link FROM task
    JOIN task_category ON task.id=task_id
    JOIN category ON category.id=category_id
    WHERE category.name = '{category}' and  task.difficulty = '{query.data}' AND task.is_in_contest=FALSE
    ORDER BY RANDOM()
    LIMIT 10
    """)

    task_set = db.cursor.fetchall()

    db.cursor.execute(f"""
        UPDATE task
        SET is_in_contest=TRUE
        WHERE id IN ({', '.join([str(elem[0]) for elem in task_set]) if task_set else -1})
        """)
    msg = '\n\n'.join([str(ind + 1) + '. ' + elem[1] + ' https://codeforces.com' + elem[2] for ind, elem in
                       enumerate(task_set)]) if task_set else "таких задач нет"
    await bot.send_message(chat_id=query.from_user.id, text=msg,
                           reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('/set_contest',
                                                                                            '/clear_all_contests'))


@dp.callback_query_handler(lambda c: c.data in categories)
async def select_tasks(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = query.data
    await bot.send_message(chat_id=query.from_user.id, text="Выберите сложность",
                           reply_markup=types.InlineKeyboardMarkup(resize_keyboard=True).add(*difficulty_buttons))


async def main():
    await dp.start_polling(bot)
