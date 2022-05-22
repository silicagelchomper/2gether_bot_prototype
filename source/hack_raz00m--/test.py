import telebot
import time
import sqlite3
import random
from telebot import types

bot = telebot.TeleBot("TOKEN_REDACTED")
conn = sqlite3.connect('test', check_same_thread=False)
cursor = conn.cursor()
current_state = 0
us_id = 0
name = ""
location = ""
profession = ""
description = ""

STATE_START = 0
USER_STATE = {
    "START": 0,
    "NAME_CHECK": 1,
    "PROFESSION_CHECK": 2,
    "LOCATION_CHECK": 3,
    "DESCRIPTION_CHECK": 4,
    "BASE_ADD": 5,
    "SEARCH_CHOICE": 6,
    "RANDOM_CHOICE": 7,
    "CRITERIAL_CHOICE": 8,
    "PROF_CHOICE": 9,
    "LOCATION_CHOICE": 10,
    "PROF_SEARCH": 11,
    "LOCATION_SEARCH": 12,
}


### ADMIN CONSOLE ###

def delete_by_current_id(user_id):
    cursor.execute("DELETE FROM test WHERE id = (?)", (user_id,))
    conn.commit()


def delete_by_custom_id(message):
    id = message.text
    id = int(id)
    cursor.execute("DELETE FROM test WHERE id = (?)", (id,))
    conn.commit()


def delete_all_base():
    cursor.execute("DELETE FROM test")
    cursor.execute("VACUUM")
    conn.commit()


def admin_console(message):
    bot.send_message(message.from_user.id, "Консоль запущена")
    if message.text == "delete":
        bot.send_message(message.from_user.id, "Удаляю текущую запись в бд")
        update_state_id(message, USER_STATE["START"])
        delete_by_current_id(message.from_user.id)
    elif message.text == "delete by id":
        bot.send_message(message.from_user.id, "Введите id пользователя, которого необходимо удалить")
        bot.register_next_step_handler(message, delete_by_custom_id)
    elif message.text == "delete all":
        bot.send_message(message.from_user.id, "Удаляю всю базу данных")
        delete_all_base()


@bot.message_handler(commands=['admin'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "Здравствуйте, добро пожаловать в админ-консоль")
    bot.send_message(message.from_user.id,
                 "Список доступных команд: delete - удалить вашу запись, delete by id - удалить запись по id, delete all - стереть ВСЮ БАЗУ ДАННЫХ")
    bot.register_next_step_handler(message, admin_console)


### АДМИН КОНСОЛЬ ЗАКОНЧИЛАСЬ ###

# случайный поиск человека
def random_search_teammate(message):
    global us_id
    data = cursor.execute('''SELECT * FROM test''')
    id_list = []
    for column in data:
        id_list.append(column)
    if len(id_list) > 1:
        teammate_id = random.choice(id_list)

        while teammate_id[0] == us_id:
            teammate_id = random.choice(id_list)
        bot.send_message(message.from_user.id, "Ваш напарник найден. Это: " + str(teammate_id))
    else:
        bot.send_message(message.from_user.id, "Поиск еще в процессе! Мы уведомим вас, когда будет готово")
        return 0
    return teammate_id


# поиск по локации
def match_user_by_location(message, location):
    response = cursor.execute('SELECT name FROM test WHERE location = (?)', (location,))
    response = response.fetchone()
    if response is None:
        bot.send_message(message.from_user.id, "Пока что подходящего человека нет")
        return None
    else:
        bot.send_message(message.from_user.id, "Под ваш запрос подходит " + str(response[0]))
        return response[0]


# поиск по профессии
def match_user_by_profession(message, search_prof):
    response = cursor.execute('SELECT name FROM test WHERE profession = (?)', (search_prof,))
    response = response.fetchone()
    if response is None:
        bot.send_message(message.from_user.id, "Пока что подходящего человека нет")
        return None
    else:
        bot.send_message(message.from_user.id, "Под ваш запрос подходит " + str(response[0]))
        return response[0]


# проверка на существование пользователя
def check_existed_id(user_id):
    response = cursor.execute('SELECT 1 FROM test WHERE id = (?)', (user_id,))
    response = response.fetchone()
    if response is None:
        return response
    else:
        print(response[0])
        return response[0]


def update_user_name(user_name, user_id):
    cursor.execute('UPDATE test SET name = (?) WHERE id = (?)', (user_name, user_id))
    conn.commit()


def update_user_profession(user_profession, user_id):
    cursor.execute('UPDATE test SET profession = (?) WHERE id =(?)', (user_profession, user_id))
    conn.commit()


def update_user_location(user_location, user_id):
    cursor.execute('UPDATE test SET location = (?) WHERE id =(?)', (user_location, user_id))
    conn.commit()


def update_user_description(user_description, user_id):
    cursor.execute('UPDATE test SET description = (?) WHERE id =(?)', (user_description, user_id))
    conn.commit()


# запись данных в базу данных
def add_user_into_bd(user_id: int, user_name: str, user_profession: str, user_location: str, user_description: str):
    update_user_name(user_name, user_id)
    update_user_profession(user_profession, user_id)
    update_user_location(user_location, user_id)
    update_user_description(user_description, user_id)


# добавить юзер айди
def add_user_id(user_id: int):
    cursor.execute("INSERT INTO test VALUES (?, ?,?,?,?,?)", (user_id, "", "", "", "", 0))
    conn.commit()


# помощь
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, "Здравствуйте! Тут список команд")


# приветствие
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "Здравствуйте, новый пользователь. Введите ваш ник: ")


# получаем state по айди
def get_state_id(message, us_id):
    response = cursor.execute('SELECT state FROM test WHERE id = (?) LIMIT 1', (us_id,))
    response = response.fetchone()
    if response is None:
        return response
    else:
        print(response[0])
        return response[0]


# получаем location по айди
def get_location_id(message, us_id):
    response = cursor.execute('SELECT location FROM test WHERE id = (?) LIMIT 1', (us_id,))
    response = response.fetchone()
    if response is None:
        return response
    else:
        print(response[0])
        return response[0]


# получаем location по айди
def get_profession_id(message, us_id):
    response = cursor.execute('SELECT profession FROM test WHERE id = (?) LIMIT 1', (us_id,))
    response = response.fetchone()
    if response is None:
        return response
    else:
        print(response[0])
        return response[0]


# устанавливаем state в значение равное value
def update_state_id(message, value):
    us_id = message.from_user.id
    cursor.execute('UPDATE test SET state = (?) WHERE id =(?)', (value, us_id))
    conn.commit()


# основное тело
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global state_dictionary, name, profession, location, description, us_id
    ### ЗАПРОС ТЕКУЩЕГО СТЕЙТА
    us_id = message.from_user.id
    # проверка айдишника
    if check_existed_id(us_id) == 1:
        current_state = get_state_id(message, us_id)
    else:
        bot.send_message(message.from_user.id, "Тут надо добавить в бд твой айди и стейт")
        add_user_id(us_id)
        current_state = get_state_id(message, us_id)

    ### ФОРМИРОВАНИЕ АНКЕТЫ
    # запрос имени
    if current_state == 0:
        update_state_id(message, USER_STATE["NAME_CHECK"])
        name = message.text
        bot.send_message(message.from_user.id, "Здравствуй, " + name + ".Введи, пожалуйста, свою профессию")
    # запрос локации
    elif current_state == 1:
        update_state_id(message, USER_STATE["PROFESSION_CHECK"])
        profession = message.text
        bot.send_message(message.from_user.id, "Спасибо! Теперь введи, пожалуйста, свой город")
    elif current_state == 2:
        update_state_id(message, USER_STATE["LOCATION_CHECK"])
        location = message.text
        bot.send_message(message.from_user.id, "Спасибо! Теперь введи описание себя")
    elif current_state == 3:
        update_state_id(message, USER_STATE["DESCRIPTION_CHECK"])
        description = message.text
        bot.send_message(message.from_user.id, "Спасибо! Добавляю тебя в базу данных :)")
        current_state = get_state_id(message, us_id)

    ### ДОБАВЛЕНИЕ В БАЗУ
    if current_state == 4:
        update_state_id(message, USER_STATE["BASE_ADD"])
        bot.send_message(message.from_user.id, "Тебя зовут " + name + " ты " + profession + " , ты живешь в " + location)
        bot.send_message(message.from_user.id, "Информация о тебе:" + description)
        add_user_into_bd(us_id, name, profession, location, description)
        bot.send_message(message.from_user.id, "Ты добавлен в базу!")
        current_state = get_state_id(message, us_id)

    ### ВЫБОР РЕЖИМА ПОИСКА + КНОПКА ИЗМЕНЕНИЯ АНКЕТЫ ###
    if current_state == 5:
        update_state_id(message, USER_STATE["SEARCH_CHOICE"])
        # кнопка рандом
        keyboard = types.InlineKeyboardMarkup()
        key_randsearch = types.InlineKeyboardButton(text='Случайный', callback_data='randsearch')
        keyboard.add(key_randsearch)
        # кнопка критерий
        key_critsearch = types.InlineKeyboardButton(text='По критериям', callback_data='critsearch')
        keyboard.add(key_critsearch)
        # вернуться на редактирование анкеты
        key_backtoinfo = types.InlineKeyboardButton(text='Редактировать анкету', callback_data='editinfo')
        keyboard.add(key_backtoinfo)
        bot.send_message(message.from_user.id, text='Выберите режим поиска:', reply_markup=keyboard)

        # обработчик кнопок
        @bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            if call.data == "randsearch":
                update_state_id(message, USER_STATE["RANDOM_CHOICE"])
                bot.send_message(message.from_user.id, text="Выбран случайный поиск.")
            elif call.data == "critsearch":
                update_state_id(message, USER_STATE["CRITERIAL_CHOICE"])
                bot.send_message(message.from_user.id, text="Выбран критериальный поиск.")
            elif call.data == "editinfo":
                user_id = message.from_user.id
                update_state_id(message, USER_STATE["START"])
                #delete_by_current_id(user_id)
                bot.send_message(message.from_user.id, text="Отлично, введи свое имя.")

        current_state = get_state_id(message, us_id)


    ### РАНДОМНЫЙ ПОИСК ###
    if current_state == 7:
        teammate_id = 0
        while teammate_id == 0:
            time.sleep(3)
            teammate_id = random_search_teammate(message)
        bot.send_message(message.from_user.id, "Поиск завершен!")

    ### КРИТЕРИАЛЬНЫЙ ПОИСК ###
    if current_state == 8:
        # кнопка проф
        keyboard = types.InlineKeyboardMarkup()
        key_randsearch = types.InlineKeyboardButton(text='Специализация', callback_data='profsearch')
        keyboard.add(key_randsearch)
        # кнопка локация
        key_critsearch = types.InlineKeyboardButton(text='Локация', callback_data='localsearch')
        keyboard.add(key_critsearch)
        bot.send_message(message.from_user.id, text="Выберите нужный критерий поиска:", reply_markup=keyboard)

        # обработчик кнопок

        @bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            if call.data == "profsearch":
                bot.send_message(message.from_user.id, text="Выбран поиск по профессии.Отправь точку, если хочешь, чтобы я взял специальность, которую ты указал в анкете. Отправь специальность, если хочешь, чтобы я искал городть")
                update_state_id(message, USER_STATE["PROF_SEARCH"])
            elif call.data == "localsearch":
                bot.send_message(message.from_user.id,
                                 text="Отправь точку, если хочешь, чтобы я взял локацию, которую ты указал в анкете. Отправь город, если хочешь, чтобы я искал город")
                update_state_id(message, USER_STATE["LOCATION_SEARCH"])
        current_state = get_state_id(message, us_id)
    current_state = get_state_id(message, us_id)
    # поиск по профессии (ян)
    if current_state == 11:
        if message.text == '.':
            us_id = message.from_user.id
            profession = get_profession_id(message, us_id)
            answer_string = "Беру вашу профессию: " + profession
            bot.send_message(message.from_user.id, answer_string)
        else:
            location = message.text
        match_user_by_profession(message, profession)
    # поиск по локации (щенок)
    if current_state == 12:
        #bot.send_message(message.from_user.id, "тут")
        if message.text == '.':
            us_id = message.from_user.id
            location = get_location_id(message, us_id)
            answer_string = "Беру вашу локацию: " + location
            bot.send_message(message.from_user.id, answer_string)
        else:
            location = message.text
        match_user_by_location(message, location)


bot.polling(none_stop=True, timeout=123)
