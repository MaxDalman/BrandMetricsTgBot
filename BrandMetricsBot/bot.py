from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Text
from aiogram.types import BotCommand
from aiogram.filters import Command
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils import keyboard
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config, load_config

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=storage)


# Создаем объекты кнопок
button_1: KeyboardButton = KeyboardButton(text='Расскажите подробнее о себе')
button_2: KeyboardButton = KeyboardButton(text='Каким образом вы гарантируете оплату?')
button_3: KeyboardButton = KeyboardButton(text='Как и в какие сроки происходит выплата?')
button_4: KeyboardButton = KeyboardButton(text='У меня остались вопросы!')
button_5: KeyboardButton = KeyboardButton(text='etc')

web_app_btn_1: KeyboardButton = KeyboardButton(
                                text='Сайт BrandMetrics',
                                web_app=WebAppInfo(url="https://www.brandmetrics.com/"))
web_app_btn_2: KeyboardButton = KeyboardButton(
                                text='Например вставить группу в соц сетях',
                                web_app=WebAppInfo(url="https://www.brandmetrics.com/"))

manager_1: KeyboardButton = KeyboardButton(text='Менеджер банковского проекта, Светлана Сергеевна Иванова')
manager_2: KeyboardButton = KeyboardButton(text='Руководитель проектов, Ирина Николаевна Петрова')


# Создаем объект клавиатуры, добавляя в него кнопки
my_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                        keyboard=[[button_1],
                                  [button_2],
                                  [button_3],
                                  [button_4],
                                  [button_5]],
                        resize_keyboard=True)

web_app_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                            keyboard=[[web_app_btn_1],
                                                      [web_app_btn_2]],
                                            resize_keyboard=True)

contacts_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                            keyboard=[[manager_1],
                                                      [manager_2]],
                                            resize_keyboard=True)

# Создаем асинхронную функцию
async def set_main_menu(bot: Bot):

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/resources',
                   description='Наши ресурсы'),
        BotCommand(command='/contacts',
                   description='Другие способы связи')]

    await bot.set_my_commands(main_menu_commands)


# Этот хэндлер будет срабатывать на команду "/start" и отправлять в чат клавиатуру
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text='Привет! 👋 \nЯ бот из BrandMetrics и ещё учусь ладить с людьми 🙈\n'
                              'Но ничего, очень скоро я найду тебя 🤖. \n'
                              'До тех пор можешь потыкаться и просмотреть что я могу. ',
                         reply_markup=my_keyboard)


# Этот хэндлер будет срабатывать на ответ "Расскажите подробнее о себе" и удалять клавиатуру
@dp.message(Text(text='Расскажите подробнее о себе'))
async def process_dog_answer(message: Message):
    await message.answer(text='Вставить текст о себе. ',
                         reply_markup=my_keyboard)


# Этот хэндлер будет срабатывать на ответ "Каким образом вы гарантируете оплату?"
@dp.message(Text(text='Каким образом вы гарантируете оплату?'))
async def process_cucumber_answer(message: Message):
    await message.answer(text='Вставить текст о гарантии оплат.\n ',
                         reply_markup=my_keyboard)

# Этот хэндлер будет срабатывать на ответ "Как и в какие сроки происходит выплата?"
@dp.message(Text(text='Как и в какие сроки происходит выплата?'))
async def process_cucumber_answer(message: Message):
    await message.answer(text='Вставить текст о порядке выплат.\n ',
                         reply_markup=my_keyboard)

# Этот хэндлер будет срабатывать на ответ "У меня остались вопросы!"
@dp.message(Text(text='У меня остались вопросы!'))
async def process_cucumber_answer(message: Message):
    await message.answer(text='Вставить текст о том, если остались вопросы.\n ',
                         reply_markup=my_keyboard)


# Этот хэндлер будет срабатывать на ответ manager_1 и удалять клавиатуру
@dp.message(Text(text='Менеджер банковского проекта, Светлана Сергеевна Иванова'))
async def process_dog_answer(message: Message):
    await message.answer(text='Вставить текст с описанием, кому стоит обращаться к данному сотруднику. \n'
                              'Контакты: 8(800)555-35-35. ',
                         reply_markup=my_keyboard)

# Этот хэндлер будет срабатывать на ответ manager_2 и удалять клавиатуру
@dp.message(Text(text='Руководитель проектов, Ирина Николаевна Петрова'))
async def process_dog_answer(message: Message):
    await message.answer(text='Вставить текст с описанием, кому стоит обращаться к данному сотруднику. \n'
                              'Контакты: 8(800)555-35-35. ',
                         reply_markup=my_keyboard)

# Этот хэндлер будет срабатывать на команду "/help" и отправлять в чат клавиатуру
@dp.message(Command(commands=["help"]))
async def process_start_command(message: Message):
    await message.answer(text='Привет ещё раз! 👋 \nЯ бот из BrandMetrics и это описание что я могу\n'
                              'Вставить описание. \n'
                              'До тех пор можешь потыкаться и просмотреть что я могу. ',
                         reply_markup=my_keyboard)

# Этот хэндлер будет срабатывать на команду "/resources"
@dp.message(Command(commands=["resources"]))
async def process_web_app_command(message: Message):
    await message.answer(text='Выберите источник',
                         reply_markup=web_app_keyboard)

# Этот хэндлер будет срабатывать на команду "/contacts"
@dp.message(Command(commands=["contacts"]))
async def process_web_app_command(message: Message):
    await message.answer(text='Выберите направление, менеджера',
                         reply_markup=contacts_keyboard)

@dp.message()
async def send_answer(message: Message):
    await message.answer(text='Извини, я тебя не понимаю 😵‍💫\n'
                              'Попробуй отвечать кнопками на клавиатуре.',
                         reply_markup=my_keyboard)

if __name__ == '__main__':
    # Регистрируем асинхронную функцию в диспетчере,
    # которая будет выполняться на старте бота,
    dp.startup.register(set_main_menu)
    # Запускаем поллинг
    dp.run_polling(bot)