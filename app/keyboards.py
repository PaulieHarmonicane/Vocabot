from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import app.database.requests as rq

modes_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Карточки')],
    [KeyboardButton(text='Тестик')],
    [KeyboardButton(text='Добавить карточку')],
    [KeyboardButton(text='В главное меню')]
])

settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='YouTube', url='https://youtube.com/@TheDickeyDinesShow')]])



async def reply_langs(tg_id):
    my_langs = await rq.my_languages(tg_id)
    keyboard = ReplyKeyboardBuilder()
    if my_langs:
        for lang in my_langs.split(','):
            keyboard.add(KeyboardButton(text=lang, callback_data=f'lang_{lang}'))
    keyboard.add(KeyboardButton(text="Добавить язык"))
    return keyboard.adjust(1).as_markup()

async def add_langs():
    all_langs = await rq.get_languages()
    keyboard = InlineKeyboardBuilder()
    for language in all_langs:
        keyboard.add(InlineKeyboardButton(text=language, callback_data=f'lang_{language}'))
    return keyboard.adjust(2).as_markup()


add_more_end = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Новая карточка', callback_data='new_card')],
    [InlineKeyboardButton(text='Закончить', callback_data='finish_adding')]
])

rep_home_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать', callback_data='repeating')],
    [InlineKeyboardButton(text='Выход', callback_data='finish_adding')]
])

test_home_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начать', callback_data='testing')],
    [InlineKeyboardButton(text='Выход', callback_data='finish_adding')]
])

known_unknown = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Знаю', callback_data='known'),
    InlineKeyboardButton(text='Не знаю', callback_data='unknown')]
])

continue_finish = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback_data='repeating'),
    InlineKeyboardButton(text='Закончить', callback_data='finish_adding')]
])

finish_test = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Закончить', callback_data='finish_adding')]
])

continue_test = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback_data='testing')]
])

home_edit_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отменить карточку')]
])

approve_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Все верно!', callback_data='approve_word')],
    [InlineKeyboardButton(text='Переделать!', callback_data='edit_card')]
])

existing_word_edit_leave = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Редактировать перевод', callback_data='add_more_meanings')],
    [InlineKeyboardButton(text='Добавить другое слово', callback_data='new_card')]
])

edit_replace_translation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Дополнить перевод', callback_data='edit_translation')],
    [InlineKeyboardButton(text='Заменить перевод', callback_data='replace_translation')]
])

async def test_which_way(current_language):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=f'{current_language} -> русский', callback_data='foreign_rus'))
    keyboard.add(InlineKeyboardButton(text=f'русский -> {current_language}', callback_data='rus_foreign'))
    keyboard.add(InlineKeyboardButton(text='Выход', callback_data='finish_adding'))
    return keyboard.adjust(2).as_markup()

async def editing_card(steps):
    keyboard = InlineKeyboardBuilder()
    for callback, step in steps:
        keyboard.add(InlineKeyboardButton(text=step, callback_data=f'inputedit:{callback}'))
    return keyboard.adjust().as_markup()



