from aiogram.types import BotCommand
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)

from aiogram.types.web_app_info import WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config, load_config


from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)


config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=storage)

#######################################################################################################################

# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодейтсвия с пользователем
    fill_name = State()        # Состояние ожидания ввода имени
    fill_city = State()        # Состояние ожидания ввода города
    fill_mail = State()        # Состояние ожидания ввода почты
    fill_phone = State()       # Состояние ожидания ввода контактного телефона


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='Вы вне состояния заполнения анкеты\n\n'
                              'Чтобы перейти к заполнению анкеты - '
                              'отправьте команду /fillform')


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Вы вышли из состояния заполнения анкеты\n\n'
                              'Чтобы снова перейти к заполнению анкеты - '
                              'отправьте команду /fillform')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода имени
@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Сейчас мы поможем оформить короткую анкету для регистрации на портале Shopmetrics. Оформление займёт не более 1 минуты.\n'
                              'Заполняя анкету Вы даёте своё согласие на обработку анкеты и Ваших персональных данных компанией BRANDMETRIKA.\n'
                              '\n'
                              'Пожалуйста, введите ваше имя, фамилию.\n'
                              'Пример: <i>Иван Иванов</i>\n'
                              '\n'
                              '<i>Если вы хотите прервать заполнение анкеты - отправьте команду</i> <b>/cancel</b>',
                         parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@dp.message(StateFilter(FSMFillForm.fill_name), lambda message: not message.text.startswith('/'))
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите ваш город проживания\n'
                              'Пример, <i>Санкт-Петербург</i>\n'
                              '\n'
                              '<i>Если вы хотите прервать заполнение анкеты - отправьте команду</i> <b>/cancel</b>',
                         parse_mode='HTML')
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_city)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(text='То, что вы отправили не похоже на имя\n\n'
                              'Пожалуйста, введите ваше имя\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если введен корректный город
# и переводить в состояние почты
@dp.message(StateFilter(FSMFillForm.fill_city), lambda message: not message.text.startswith('/'))
async def process_city_sent(message: Message, state: FSMContext):
    # Cохраняем город в хранилище по ключу "city"
    await state.update_data(city=message.text)
    # Отправляем пользователю сообщение
    await message.answer(text='Спасибо!\nУкажите вашу электронную почту\n'
                              '\n'
                              'Пример, <i>example@mail.ru</i>\n'
                              '\n'
                              '<i>Если вы хотите прервать заполнение анкеты - отправьте команду</i> <b>/cancel</b>',
                         parse_mode='HTML')
    # Устанавливаем состояние ожидания указания города
    await state.set_state(FSMFillForm.fill_mail)


# Этот хэндлер будет срабатывать, если во время ввода города
# будет введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_city))
async def warning_not_city(message: Message):
    await message.answer(
        text='Введите, пожалуйста, населённый пункт проживания\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если во время написания города
# будет введено/отправлено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_city))
async def warning_not_city(message: Message):
    await message.answer(text='Пожалуйста, укажите ваш населённый пункт проживания\n\nЕсли вы хотите прервать '
                              'заполнение анкеты - отправьте команду /cancel')


# Этот хэндлер будет срабатывать, если отправлена почта
# и переводить в состояние указания телефона
@dp.message(StateFilter(FSMFillForm.fill_mail), Text(contains='@'))
async def process_mail_sent(message: Message, state: FSMContext):
    # Cохраняем почту в хранилище по ключу "mail"
    await state.update_data(mail=message.text)
    # Отправляем пользователю сообщение
    await message.answer(text='Спасибо!\n\nУкажите ваш контактный телефон.\n'
                              'Пример, <i>+7 777 777 77 77</i>\n'
                              '\n'
                              '<i>Если вы хотите прервать заполнение анкеты - отправьте команду </i><b>/cancel</b>',
                         parse_mode='HTML')
    # Устанавливаем состояние ожидания указания телефона
    await state.set_state(FSMFillForm.fill_phone)


# Этот хэндлер будет срабатывать, если во время отправки почты
# будет введено/отправлено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_mail))
async def warning_not_mail(message: Message):
    await message.answer(text='Пожалуйста, на этом шаге укажите '
                              'вашу электронную почту.\n\nЕсли вы хотите прервать '
                              'заполнение анкеты - отправьте команду /cancel')


# Этот хэндлер будет срабатывать на заполнение телефона и выводить из машины состояний
@dp.message(StateFilter(FSMFillForm.fill_phone), lambda message: not message.text.startswith('/'))
async def process_phone_sent(message: Message, state: FSMContext):
    # Cохраняем телефон в хранилище по ключу "phone"
    await state.update_data(phone=message.text)
    # Добавляем в "базу данных" анкету пользователя
    # по ключу id пользователя
    user_dict[message.from_user.id] = await state.get_data()
    # Завершаем машину состояний
    await state.clear()
    # # Отправляем в чат сообщение с предложением посмотреть свою анкету
    # await message.answer(text='Отлично! Ваша анкета сформирована!\n'
    #                           'Чтобы проверить данные вашей анкеты и перейти в следующему шагу - отправьте команду /showdata')
    if message.from_user.id in user_dict:
        await message.answer(
               text='Отлично! Ваша анкета сформирована!\n'
                    '\n'
                    'Пожалуйста, убедитесь в корректности данных 📝\n'
                    '\n'
                    f'🕵️ <b>Имя, Фамилия</b>: {user_dict[message.from_user.id]["name"]}\n'
                    f'🏠 <b>Город</b>: {user_dict[message.from_user.id]["city"]}\n'
                    f'📧 <b>Эл.почта</b>: {user_dict[message.from_user.id]["mail"]}\n'
                    f'📲 <b>Контактный телефон:</b> {user_dict[message.from_user.id]["phone"]}\n',
               parse_mode='HTML')
        await message.answer(text='Отправить анкету на регистрацию в качестве Тайного Покупателя компании <b>BRANDMETRIKA</b> на портале <i>Shopmetrics</i>?',
                         parse_mode='HTML',
                         reply_markup=send_form_keyboard)


# Этот хэндлер будет срабатывать, если при вводе телефона было введено что-то некорректное
@dp.message(StateFilter(FSMFillForm.fill_phone))
async def warning_not_phone(message: Message):
    await message.answer(text='Пожалуйста, укажите ваш контактный номер телефона.\n\n'
                              'Если вы хотите прервать заполнение анкеты - '
                              'отправьте команду /cancel')


# # Этот хэндлер будет срабатывать на отправку команды /showdata
# # и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
# @dp.message(Command(commands='showdata'))
# async def process_showdata_command(message: Message):
#     # Отправляем пользователю анкету, если она есть в "базе данных"
#     if message.from_user.id in user_dict:
#         await message.answer(
#                text='Пожалуйста, убедитесь в корректности данных 📝:\n'
#                     '\n'
#                     f'<b>Имя, Фамилия</b>: {user_dict[message.from_user.id]["name"]}\n'
#                     f'<b>Город</b>: {user_dict[message.from_user.id]["city"]}\n'
#                     f'<b>Эл.почта</b>: {user_dict[message.from_user.id]["mail"]}\n'
#                     f'<b>Контактный телефон:</b> {user_dict[message.from_user.id]["phone"]}\n',
#                parse_mode='HTML')
#         await message.answer(text='Отправить анкету на регистрацию в качестве Тайного Покупателя компании <b>BRANDMETRIKA</b> на портале <i>Shopmetrics</i>?',
#                          parse_mode='HTML',
#                          reply_markup=send_form_keyboard)
#     else:
#         # Если анкеты пользователя в базе нет - предлагаем заполнить
#         await message.answer(text='Вы еще не заполняли анкету. '
#                                   'Чтобы приступить - отправьте '
#                                   'команду /fillform')

########################################################################################################################

# Создаем объекты инлайн-кнопок
inline_button_yes: InlineKeyboardButton = InlineKeyboardButton(
    text='Да',
    callback_data='inline_button_yes_pressed')

inline_button_no: InlineKeyboardButton = InlineKeyboardButton(
    text='Нет',
    callback_data='inline_button_no_pressed')

inline_button_send_form: InlineKeyboardButton = InlineKeyboardButton(
    text='Отправить на регистрацию',
    callback_data='inline_button_send_pressed')

inline_button_dont_send_form: InlineKeyboardButton = InlineKeyboardButton(
    text='Не отправлять',
    callback_data='inline_button_dont_send_pressed')

# Создаем объект инлайн-клавиатуры
start_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[inline_button_yes],
                     [inline_button_no]])

send_form_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[[inline_button_send_form],
                     [inline_button_dont_send_form]])


# Создаем объекты кнопок
button_yes: KeyboardButton = KeyboardButton(text='Да')
button_no: KeyboardButton = KeyboardButton(text='Нет')

button_1: KeyboardButton = KeyboardButton(text='📄 Каким образом Вы гарантируете оплату?')
button_2: KeyboardButton = KeyboardButton(text='💸 Как и в какие сроки происходит выплата?')
button_3: KeyboardButton = KeyboardButton(text='🔎 Как я могу начать работать Тайным покупателем в компании BRANDMETRIKA?')
button_4: KeyboardButton = KeyboardButton(text='📝 Другой вопрос.')

web_app_btn_1: KeyboardButton = KeyboardButton(
                                text='Сайт BrandMetrics',
                                web_app=WebAppInfo(url="https://www.brandmetrics.com/"))
web_app_btn_2: KeyboardButton = KeyboardButton(
                                text='Например вставить группу в соц сетях',
                                web_app=WebAppInfo(url="https://www.brandmetrics.com/"))

manager_1: KeyboardButton = KeyboardButton(text='Менеджер банковского проекта, Светлана Сергеевна Иванова')
manager_2: KeyboardButton = KeyboardButton(text='Руководитель проектов, Ирина Николаевна Петрова')


# Создаем объект клавиатуры, добавляя в него кнопки
# start_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
#                                             keyboard=[[button_yes],
#                                                       [button_no]],
#                                             resize_keyboard=True)

faq_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                        keyboard=[[button_1],
                                  [button_2],
                                  [button_3],
                                  [button_4]],
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
        BotCommand(command='/start',
                   description='Запуск бота'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        # BotCommand(command='/resources',
        #            description='Наши ресурсы'),
        BotCommand(command='/contacts',
                   description='Другие способы связи'),
        BotCommand(command='/fillform',
                   description='Начать оформление анкеты'),
        BotCommand(command='/cancel',
                   description='Выйти из оформления анкеты')]

    await bot.set_my_commands(main_menu_commands)


# Этот хэндлер будет срабатывать на команду "/start" и отправлять в чат клавиатуру
@dp.message(CommandStart())
async def process_start_command(message: Message):
# Выводит в консоль апдейт пользователя, попавшего в этот хендлер
    #print(message.json(indent=4, exclude_none=True))
    await message.answer(text='Здравствуйте! \n'
                              'Вы уже зарегистрированы в качестве Тайного Покупателя\n'
                              'компании <b>BRANDMETRIKA</b> на портале <i>Shopmetrics</i>?\n',
                         parse_mode='HTML',
                         reply_markup=start_keyboard)


# Этот хэндлер будет срабатывать на ответ "Да" и открывать меню вопросов
@dp.callback_query(Text(text=['inline_button_yes_pressed'], ignore_case=True))
async def process_yes_answer(message: Message):
    await bot.send_message(message.from_user.id, 'Отлично! 😊\n'
                              'Выберите Ваш вопрос в главном меню.\n'
                              'Буду рад Вам помочь!',
                         reply_markup=faq_keyboard)


# Этот хэндлер будет срабатывать на ответ "Нет" и открывать меню вопросов
@dp.callback_query(Text(text=['inline_button_no_pressed'], ignore_case=True))
async def process_no_answer(message: Message):
    await bot.send_message(message.from_user.id, 'Ничего страшного!\n'
                              'Давайте я Вам помогу 😊\n'
                              '\n'
                              'Для оформления заявки на регистрацию, пожалуйста, введите команду /fillform\n',
                         reply_markup=faq_keyboard)


# @dp.callback_query(Text(text=['inline_button_yes_pressed']))
# async def process_yes_answer(message: Message):
#     await message.answer(text='Отлично! 😊\n'
#                               'Выберите Ваш вопрос в главном меню.\n'
#                               'Буду рад Вам помочь!',
#                          reply_markup=faq_keyboard)
#
#
# # Этот хэндлер будет срабатывать на ответ "Нет" и открывать меню вопросов
# @dp.callback_query(Text(text=['inline_button_no_pressed']))
# async def process_no_answer(message: Message):
#     await message.answer(text='Ничего страшного!\n'
#                               'Давайте я Вам помогу 😊\n'
#                               '\n'
#                               'Для оформления заявки на регистрацию, пожалуйста, введите команду /fillform\n',
#                          reply_markup=faq_keyboard)


# Этот хэндлер будет срабатывать на апдейт типа CallbackQuery
# с data 'inline_button_send_pressed' и переправлять сообщение менеджеру
@dp.callback_query(Text(text=['inline_button_send_pressed']))
async def process_send_form_manager(message: Message):
    # Отправляем менеджеру анкету, если она есть в "базе данных"
    if message.from_user.id in user_dict:
        await bot.send_message(275668298,
               text='Привет! Необходимо зарегистрировать нового агента в Shopmetrics 🕵‍\n'
                    '\n'
                    f'<b>🕵️ Имя, Фамилия</b>: {user_dict[message.from_user.id]["name"]}\n'
                    f'<b>🏠 Город</b>: {user_dict[message.from_user.id]["city"]}\n'
                    f'<b>📧 Эл.почта</b>: {user_dict[message.from_user.id]["mail"]}\n'
                    f'<b>📲 Контактный телефон:</b> {user_dict[message.from_user.id]["phone"]}\n'
                    '\n'
                    'Спасибо',
               parse_mode='HTML')
        await bot.send_message(message.from_user.id, 'Спасибо!\n'
                                  '\n'
                                  'В начале следующего рабочего дня Вы сможете войти в свой личный кабинет на платформе по ссылке:\n'
                                  'https://brandmetrika.shopmetrics.com\n'
                                  '\n'
                                  'Ваш <i><b>логин для входа</b></i> - это <i><b>адрес Вашей эл.почты</b></i>\n'
                                  'Ваш <i><b>пароль</b></i> – это <i><b>Ваша фамилия</b></i> 😊',
                         parse_mode='HTML',
                         reply_markup=faq_keyboard)


# Этот хэндлер будет срабатывать на ответ с data 'inline_button_dont_send_pressed' и предлагать перезаполнить анкету
@dp.callback_query(Text(text=['inline_button_dont_send_pressed']))
async def process_dont_send_manager(message: CallbackQuery):
    await bot.send_message(message.from_user.id, 'Хорошо!\n'
                              'Эти данные никуда не будут отправлены.\n'
                              '\n'
                              'Для пересоздания заявки на регистрацию, введите команду /fillform\n',
                         reply_markup=faq_keyboard)

# Этот хэндлер будет срабатывать на ответ "📄 Каким образом Вы гарантируете оплату?"
@dp.message(Text(text='📄 Каким образом Вы гарантируете оплату?'))
async def process_payment(message: Message):
    await message.answer(text='Гарантийное письмо, имеющее юридическую силу, по запросу можно получить у координатора проекта, который назначил (-назначает) Вам проверку.',
                         reply_markup=faq_keyboard)

# Этот хэндлер будет срабатывать на ответ "💸 Как и в какие сроки происходит выплата?"
dp.message(Text(text='💸 Как и в какие сроки происходит выплата?'))
async def process_duration_payment(message: Message):
    await message.answer(text='Платежная ведомость формируется к 10му числу следующего месяца. '
                              'В этот день вы получите письмо-рассылку, которое будет содержать Вашу итоговую сумму заработка за прошедший месяц. '
                              'И, если проверки вы делаете у нас впервые, письмо приглашение присоединиться к нашей команде в <a href="https://qugo.ru/">Qugo</a> или <a href="https://solarstaff.com/freelancer/invitation">Solar Staff</a>. '
                              'На платформах Вам будут выставлены задачи, которые нужно будет принять и завершить.\n'
                              '\n'
                              'Пример: \n'
                              'Вы провели проверки 1, 10, 12 и 25 августа. Данные проверки будут включены в платёжную ведомость 10 сентября. '
                              'В этот же день Вы получите письмо на электронную почту с итоговой суммой оплаты по этим проверкам. '
                              'Во временной промежуток с 11 сентября до 20 октября Вам будут выставлены задачи в выбранной вами платежной системе и начислены денежные средства.',
                         parse_mode='HTML',
                         reply_markup=faq_keyboard)

# Этот хэндлер будет срабатывать на ответ "🔎 Как я могу начать работать Тайным покупателем в компании BRANDMETRIKA?"
@dp.message(Text(text='🔎 Как я могу начать работать Тайным покупателем в компании BRANDMETRIKA?'))
async def process_want_be_agent(message: Message):
    await message.answer(text='Для начала работы Тайным Покупателем в компании BRANDMETRIKA Вам нужно зарегистрироваться на платформе Shopmetrics по ссылке:\n'
                              'https://brandmetrika.shopmetrics.com/auth/index.asp#signup',
                         reply_markup=faq_keyboard)

# Этот хэндлер будет срабатывать на ответ "📩 Я провёл проверку, не получается загрузить материалы/отправить анкету."
@dp.message(Text(text='📩 Я провёл проверку, не получается загрузить материалы/отправить анкету.'))
async def process_cant_upload(message: Message):
    await message.answer(text='Пожалуйста, обратитесь к Вашему Координатору – он обязательно Вам поможет с отправкой материалов!',
                         reply_markup=faq_keyboard)

# Этот хэндлер будет срабатывать на ответ "📝 Другой вопрос."
@dp.message(Text(text='📝 Другой вопрос.'))
async def process_another_question(message: Message):
    await message.answer(text='Пожалуйста, обратитесь к Вашему Координатору проекта напрямую или же направьте свой вопрос на эл. почту:\n'
                              'info@brandmetrika.ru',
                         reply_markup=faq_keyboard)


# # Этот хэндлер будет срабатывать на ответ manager_1 и удалять клавиатуру
# @dp.message(Text(text='Менеджер банковского проекта, Светлана Сергеевна Иванова'))
# async def process_dog_answer(message: Message):
#     await message.answer(text='Вставить текст с описанием, кому стоит обращаться к данному сотруднику. \n'
#                               'Контакты: 8(800)555-35-35. ',
#                          reply_markup=faq_keyboard)
#
# # Этот хэндлер будет срабатывать на ответ manager_2 и удалять клавиатуру
# @dp.message(Text(text='Руководитель проектов, Ирина Николаевна Петрова'))
# async def process_dog_answer(message: Message):
#     await message.answer(text='Вставить текст с описанием, кому стоит обращаться к данному сотруднику. \n'
#                               'Контакты: 8(800)555-35-35. ',
#                          reply_markup=faq_keyboard)

# Этот хэндлер будет срабатывать на команду "/help" и отправлять в чат клавиатуру
@dp.message(Command(commands=["help"]))
async def process_help_command(message: Message):
    await message.answer(text='Привет ещё раз! 👋 \nЯ бот из BRANDMETRIKA и моя задача предоставить полную информацию по работе Тайным покупателем.\n'
                              'Выбери интересующий тебя вопрос из меню.',
                         reply_markup=faq_keyboard)

# # Этот хэндлер будет срабатывать на команду "/resources"
# @dp.message(Command(commands=["resources"]))
# async def process_web_app_command(message: Message):
#     await message.answer(text='Выберите источник',
#                          reply_markup=web_app_keyboard)

# Этот хэндлер будет срабатывать на команду "/contacts"
@dp.message(Command(commands=["contacts"]))
async def process_contacts_command(message: Message):
    await message.answer(text='E-mail: info@brandmetrika.ru\n'
                              'Тел: +7 (800) 350-11-36\n'
                              '<a href="https://t.me/+tU8pYA1E3rw0MWQy">Telegram-канал</a>',
                         parse_mode='HTML',
                         reply_markup=contacts_keyboard)

@dp.message()
async def send_answer(message: Message):
    await message.answer(text='Извини, я тебя не понимаю 😵‍💫\n'
                              'Попробуй отвечать кнопками на клавиатуре.',
                         reply_markup=faq_keyboard)

if __name__ == '__main__':
    # Регистрируем асинхронную функцию в диспетчере,
    # которая будет выполняться на старте бота,
    dp.startup.register(set_main_menu)
    # Запускаем поллинг
    dp.run_polling(bot)