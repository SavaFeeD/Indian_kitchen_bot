import pickle
import pandas as pd
import numpy as np
import telebot

from pyTelegramBotAPI.telebot import types


class Schema:
    def create(self):
        return {
            'prep_time': [0],
            'cook_time': [0],
            'diet_non vegetarian': [0],
            'diet_vegetarian': [0],
            'flavor_profile_bitter': [0],
            'flavor_profile_sour': [0],
            'flavor_profile_spicy': [0],
            'flavor_profile_sweet': [0],
            'course_dessert': [0],
            'course_main course': [0],
            'course_snack': [0],
            'course_starter': [0]
        }


schema = {'data': {}}

# Bot
token = '1405167968:AAEFcFArarrd3BMrxzp-K2v8ld0KKDBDcSU'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'go'])
def echo_msg(message):
    start_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    start_markup_btn1 = types.KeyboardButton('Начать выбор блюда!')
    start_markup.add(start_markup_btn1)

    bot.send_message(message.chat.id, '<b>Привет!</b>', parse_mode='html', reply_markup=start_markup)


@bot.message_handler(content_types=['text'])
def router_mess(message):
    get_message_bot = message.text.strip()

    if get_message_bot == 'Начать выбор блюда!':
        schema['data'] = Schema().create()
        setDiet(message)


def setDiet(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    diet_vega = types.InlineKeyboardButton('Веган', callback_data='vega')
    diet_no_vega = types.InlineKeyboardButton('Все равно', callback_data='no_vega')

    markup.add(diet_vega, diet_no_vega)
    bot.send_message(message.chat.id, 'Какая диета интересует:', parse_mode='html', reply_markup=markup)


def setFlavor(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    flavor_sweet = types.InlineKeyboardButton('Сладкий', callback_data='sweet')
    flavor_bitter = types.InlineKeyboardButton('Горький', callback_data='bitter')
    flavor_spicy = types.InlineKeyboardButton('Острый', callback_data='spicy')
    flavor_sour = types.InlineKeyboardButton('Кислый', callback_data='sour')

    markup.add(flavor_sweet, flavor_bitter, flavor_spicy, flavor_sour)
    bot.send_message(message.chat.id, 'Какой вкус:', parse_mode='html', reply_markup=markup)


def setCourse(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    course_main = types.InlineKeyboardButton('Главное', callback_data='main course')
    course_starter = types.InlineKeyboardButton('Первое', callback_data='starter')
    course_snack = types.InlineKeyboardButton('Закуска', callback_data='snack')
    course_dessert = types.InlineKeyboardButton('Десерт', callback_data='dessert')

    markup.add(course_main, course_starter, course_snack, course_dessert)
    bot.send_message(message.chat.id, 'Какой тип блюда:', parse_mode='html', reply_markup=markup)


def setPrepTime(message):
    chat_id = message.chat.id
    text = message.text
    if not text.isdigit():
        msg = bot.send_message(chat_id, 'Время должно быть числом, введите ещё раз.')
        bot.register_next_step_handler(msg, setPrepTime)
        return
    else:
        schema['data']['prep_time'] = [text]
        msg = bot.send_message(chat_id, 'Введите сколько должно оно готовиться в минутах:')
        bot.register_next_step_handler(msg, setCookTime)


def setCookTime(message):
    chat_id = message.chat.id
    text = message.text
    if not text.isdigit():
        msg = bot.send_message(chat_id, 'Время должно быть числом, введите ещё раз.')
        bot.register_next_step_handler(msg, setPrepTime)
        return
    else:
        schema['data']['cook_time'] = [text]
        msg = bot.send_message(chat_id, '<b>Подождите немного..</b>', parse_mode='html')
        getFood(msg)


def getFood(message):
    model = pickle.load(open('indian_kitchen.sav', 'rb'))
    df = pd.DataFrame(schema['data'])
    result = model.predict(df)
    result_proba = model.predict_proba(df)
    bot.send_message(message.chat.id, f'<b><u>Ваше индийское блюдо:</u></b>\nНазвание: {result[0][1]}'
                                      f' ({round(np.amax(result_proba[1]) * 100, 1)}%)\nРегион: {result[0][0]}'
                                      f' ({round(np.amax(result_proba[0]) * 100, 1)}%)',
                     parse_mode='html')


def to_void_msg(v_bot, v_call, v_msg):
    v_bot.edit_message_text(chat_id=v_call.message.chat.id, message_id=v_call.message.message_id,
                            text=v_msg, parse_mode='html', reply_markup=None)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            # Diet
            if call.data == 'vega':
                schema['data']['diet_vegetarian'] = [1]
                bot.send_message(call.message.chat.id, 'Оу, веган', parse_mode='html')
                to_void_msg(bot, call, '<b>Привет</b>, какая диета интересует:')
                setFlavor(call.message)

            elif call.data == 'no_vega':
                schema['data']['diet_non vegetarian'] = [1]
                bot.send_message(call.message.chat.id, 'Оу, трупоед', parse_mode='html')
                to_void_msg(bot, call, '<b>Привет</b>, какая диета интересует:')
                setFlavor(call.message)

            # Flavor
            elif call.data == 'sweet':
                schema['data']['flavor_profile_sweet'] = [1]
                to_void_msg(bot, call, 'Какой вкус:')
                setCourse(call.message)

            elif call.data == 'bitter':
                schema['data']['flavor_profile_bitter'] = [1]
                to_void_msg(bot, call, 'Какой вкус:')
                setCourse(call.message)

            elif call.data == 'spicy':
                schema['data']['flavor_profile_spicy'] = [1]
                to_void_msg(bot, call, 'Какой вкус:')
                setCourse(call.message)

            elif call.data == 'sour':
                schema['data']['flavor_profile_sour'] = [1]
                to_void_msg(bot, call, 'Какой вкус:')
                setCourse(call.message)

            # Course
            elif call.data == 'main course':
                schema['data']['course_main course'] = [1]
                to_void_msg(bot, call, 'Какой тип блюда:')
                msg = bot.send_message(call.message.chat.id,
                                       'Введите примерно сколько надо времени для подготовки перед готовкой этого '
                                       'блюда в минутах:')
                bot.register_next_step_handler(msg, setPrepTime)

            elif call.data == 'starter':
                schema['data']['course_starter'] = [1]
                to_void_msg(bot, call, 'Какой тип блюда:')
                msg = bot.send_message(call.message.chat.id,
                                       'Введите примерно сколько надо времени для подготовки перед готовкой этого '
                                       'блюда в минутах:')
                bot.register_next_step_handler(msg, setPrepTime)

            elif call.data == 'snack':
                schema['data']['course_snack'] = [1]
                to_void_msg(bot, call, 'Какой тип блюда:')
                msg = bot.send_message(call.message.chat.id,
                                       'Введите примерно сколько надо времени для подготовки перед готовкой этого '
                                       'блюда в минутах:')
                bot.register_next_step_handler(msg, setPrepTime)

            elif call.data == 'dessert':
                schema['data']['course_dessert'] = [1]
                to_void_msg(bot, call, 'Какой тип блюда:')
                msg = bot.send_message(call.message.chat.id,
                                       'Введите примерно сколько надо времени для подготовки перед готовкой этого '
                                       'блюда в минутах:')
                bot.register_next_step_handler(msg, setPrepTime)

    except Exception as e:
        print(repr(e))


bot.polling(none_stop=True)

