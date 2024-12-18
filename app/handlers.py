from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.filters.state import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from app.middleware import TestMiddleware as tm
import app.keyboards as kb
import app.database.requests as rq

from app.config.config import admin_id

from app.representation import representation as repres

from aiogram.types import ReplyKeyboardRemove

import random
import re


router = Router()

router.message.middleware(tm())

class Reg(StatesGroup):
    tg_id = State()
    name = State()

class Flow(StatesGroup):
    tg_id = State()
    language = State()
    mode = State()  
    practicing = State()
    add_word = State()
    card_rep = State()
    card_test = State()
    test_cardset = State()
    test_answer = State()
    test_counter = State()
    test_wn = State()
    current_cardset = State()
    current_rate = State()
    add_transcription = State()
    add_translation = State()
    add_rate = State()
    edition = State()
    wait = State()



    
#---------STARTING HERE---------#

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if await rq.check_user(message.from_user.id) == 'New':
        await state.update_data(tg_id=message.from_user.id)
        await state.set_state(Reg.name)
        await message.answer("Enter your name")

    else:
        await message.answer(f"Добро пожаловать, {await rq.get_user_name(message.from_user.id)}!",      reply_markup=await kb.reply_langs(message.from_user.id))
        #await message.answer(text='Добавьте нужные языки!', reply_markup=await kb.reply_langs(message.from_user.id))
        await state.set_state(Flow.tg_id)
        await state.update_data(tg_id=message.from_user.id)
        await state.set_state(Flow.language)
        data_n = await state.get_data()
        print(data_n)

@router.message(Reg.name)
async def reg_fin(message: Message, state :FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await rq.set_user(data['tg_id'], data['name'])
    await state.clear()
    await message.answer(f"Регистрация завершена! \nИмя: {data['name']} \n\nДобро пожаловать! \n\nДобавьте язык!", reply_markup=await kb.reply_langs(message.from_user.id))
    await state.set_state(Flow.tg_id)
    await state.update_data(tg_id=message.from_user.id)
    await state.set_state(Flow.language)



#---------LANGUAGES---------#

@router.message(Flow.language, F.text.casefold() == 'добавить язык')
async def all_langs_list(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer(text='Какой язык вы хотите добавить?', reply_markup=await kb.add_langs())
    await state.set_state(Flow.language)

@router.callback_query(F.data.startswith('lang_'))
async def add_language(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    await rq.list_lang(callback.data.split("_")[1], callback.from_user.id)
    await callback.message.answer(text=f"Вы добавили {callback.data.split('_')[1]}!", reply_markup=await kb.reply_langs(callback.from_user.id))
    await state.set_state(Flow.language)

@router.message(Flow.language, F.text.casefold() == '中文')
async def choosing_chinese(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await state.set_state(Flow.mode)
    await message.answer("Займемся китайским!", reply_markup=kb.modes_menu)

@router.message(Flow.language, F.text.casefold() == 'english')
async def choosing_english(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await state.set_state(Flow.mode)
    await message.answer("Займемся английским!", reply_markup=kb.modes_menu)

@router.message(Flow.language, F.text.casefold() == 'español')
async def choosing_english(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await state.set_state(Flow.mode)
    await message.answer("Займемся испанским!", reply_markup=kb.modes_menu)



#---------MODES---------#

@router.message(Flow.mode, F.text.casefold() == 'в главное меню')
async def to_homepage(message: Message, state: FSMContext):
    await state.update_data(mode=message.text)
    await state.set_state(Flow.language)
    await message.answer(text='<-',reply_markup=await kb.reply_langs(message.from_user.id))

@router.message(F.text.casefold() == 'отменить карточку', StateFilter(Flow.mode, Flow.add_word, Flow.add_transcription, Flow.add_translation, Flow.edition))
async def cancel_card(message: Message, state: FSMContext):
    cd = await state.get_data()
    to_menu = {state.state.split(':')[1]:cd.get(state.state.split(':')[1]) for state in Flow.__all_states__[0:2]}
    print(to_menu)

    await state.clear()
    await state.set_state(Flow.mode)
    await state.update_data(**to_menu)
    await message.answer(text='Выбери режим', reply_markup = kb.modes_menu)

@router.message(Flow.mode, F.text.casefold() == 'добавить карточку')
async def add_flashcard(message: Message, state: FSMContext):
    await state.update_data(mode=message.text)
    await state.set_state(Flow.add_word)
    await message.answer(text='Введите слово на иностранном языке', reply_markup=kb.home_edit_button)

#---------ADDING_VOCAB---------#

@router.message(Flow.add_word)
async def adding_word(message: Message, state: FSMContext):
    current = await state.get_data()
    await state.update_data(add_word=message.text)
    all_words = [[word[0], word[1].casefold()] for word in await rq.all_words_list(current['language'])]
    print(all_words)
    print(message.text)
    if ([message.from_user.id, message.text.casefold()] in all_words):
        await message.answer('Это слово уже есть в твоей коллекции', reply_markup=kb.existing_word_edit_leave)

    else:
        await state.update_data(add_word=message.text)
        if await rq.check_if_need_transcr(current['language']) == 't':
            await state.set_state(Flow.add_transcription)
            await message.answer(text='Введите транскрипцию!')
        elif await rq.check_if_need_transcr(current['language']) == 'nt':
            await state.set_state(Flow.add_translation)
            await state.update_data(add_transcription=None)
            await message.answer(text='Введите перевод!')

@router.callback_query(F.data == 'add_more_meanings')
async def add_more_meanings(callback: CallbackQuery, state: FSMContext):
    current = await state.get_data()
    current_translation = await rq.translation_data(current['language'], current['add_word'])
    await state.set_state(Flow.wait)
    await callback.message.edit_text(text=f"Язык: {current['language']} \nСлово: {current['add_word']} \nПеревод: {current_translation}", reply_markup = kb.edit_replace_translation)

@router.callback_query(F.data == 'edit_translation')
async def add_translations(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Flow.edition)
    await state.update_data(edition='редактировать')
    await callback.message.edit_text(text='Введите, что бы вы хотели добавить к переводу')

@router.callback_query(F.data == 'replace_translation')
async def repl_translations(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Flow.edition)
    await state.update_data(edition='заменить')
    await callback.message.edit_text(text='Введите все данные по новому переводу')

@router.message(Flow.edition)
async def input_translation_data1(message: Message, state: FSMContext):
    cd = await state.get_data()
    if cd['edition'] == 'заменить':
        await rq.edit_translation_rq(cd['language'], cd['add_word'], message.text)
    elif cd['edition'] == 'редактировать':
        ct = await rq.translation_data(cd['language'], cd['add_word'])
        print(ct)
        await rq.edit_translation_rq(cd['language'], cd['add_word'], f'{ct}, {message.text}')
    
    await message.answer('Перевод отредактирован! \nСоздать новое слово?', reply_markup=kb.add_more_end)


@router.message(Flow.add_transcription)
async def adding_transcription(message: Message, state:FSMContext):
    await state.update_data(add_transcription=message.text)
    await state.set_state(Flow.add_translation)
    await message.answer(text='Введите перевод')

@router.message(Flow.add_translation)
async def adding_translation(message: Message, state: FSMContext):
    await state.update_data(add_translation=message.text)
    await state.update_data(add_rate=1)
    cd = await state.get_data()
    print(cd)
    if await rq.check_if_need_transcr(cd['language']) == 't':
        f_text = f"Слово: {cd['add_word']}, \nТранскрипция: {cd['add_transcription']}, \nПеревод: {cd['add_translation']} \n\n Добавить слово?"   
        await message.answer(text=f_text, reply_markup=kb.approve_button)
    elif await rq.check_if_need_transcr(cd['language']) == 'nt':
        f_text = f"Язык: {cd['language']}, \nСлово: {cd['add_word']}, \nПеревод: {cd['add_translation']} \n\n Добавить слово?"   
        await message.answer(text=f_text, reply_markup=kb.approve_button)
    
@router.callback_query(F.data == 'approve_word')  
async def add_final_step(callback: CallbackQuery, state: FSMContext):
    cd = await state.get_data()
    if await rq.check_if_need_transcr(cd['language']) == 't':
        await rq.add_new_card(cd['tg_id'], cd['language'], cd['add_word'], cd['add_transcription'], cd['add_translation'], cd['add_rate'])
    elif await rq.check_if_need_transcr(cd['language']) == 'nt':
        await rq.add_new_card(cd['tg_id'], cd['language'], cd['add_word'], None, cd['add_translation'], cd['add_rate'])
    await callback.message.answer(text='Что дальше?', reply_markup=kb.add_more_end)

@router.callback_query(F.data == 'edit_card')
async def edit_card(callback: CallbackQuery, state: FSMContext):
    cd = await state.get_data()
    to_beginning = {state.state.split(':')[1]:cd.get(state.state.split(':')[1]) for state in Flow.__all_states__[0:2]}
    print(to_beginning)

    await state.clear()
    await state.set_state(Flow.add_word)
    await state.update_data(**to_beginning)
    await callback.message.answer(text='Введите слово на иностранном языке')


@router.callback_query(F.data == 'new_card')
async def more_cards(callback: CallbackQuery, state: FSMContext):
    cd = await state.get_data()
    to_beginning = {state.state.split(':')[1]:cd.get(state.state.split(':')[1]) for state in Flow.__all_states__[0:3]}
    print(to_beginning)

    await state.clear()
    await state.set_state(Flow.add_word)
    await state.update_data(**to_beginning)
    await callback.message.answer(text='Введите слово на иностранном языке')

@router.callback_query(F.data == 'finish_adding')
async def finish_adding(callback: CallbackQuery, state: FSMContext):
    cd = await state.get_data()
    to_menu = {state.state.split(':')[1]:cd.get(state.state.split(':')[1]) for state in Flow.__all_states__[0:2]}
    print(to_menu)

    await state.clear()
    await state.set_state(Flow.mode)
    await state.update_data(**to_menu)
    await callback.message.answer(text='Выбери режим', reply_markup = kb.modes_menu)


#---------REPEATING_CARDS---------#

@router.message(Flow.mode, F.text.casefold() == 'карточки')
async def add_flashcard(message: Message, state: FSMContext):
    cd = await state.get_data()
    await state.update_data(mode=message.text)
    await state.set_state(Flow.card_rep)
    await message.answer(text='Сейчас перед тобой будут появляться карточки с иностранными словами. Тебе нужно честно отвечать, знаешь ли ты перевод этих слов и их произношение. Так или иначе, ты увидишь обратную сторону карточки с ответом, но если ты ответишь, что слово тебе знакомо, оно будет реже появляться для повторения.', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Начать повторение?', reply_markup=kb.rep_home_button)

@router.callback_query(F.data == 'repeating')
async def creating_card_set(callback: CallbackQuery, state:FSMContext):
    cd = await state.get_data()
    cards = await rq.get_data_to_create_cards(cd['language'], cd['tg_id'])
    all_cards = {card[0:]: card[0] for card in cards}
    keys=list(all_cards.keys())
    values=list(all_cards.values())
    current_card = random.choices(keys, weights=values, k=1)
    await state.update_data(current_cardset=current_card)
    flashcard_img = await repres.create_flashcard_question(current_card[0][1], await rq.check_if_need_transcr(cd['language']), cd['language'])
    photo = BufferedInputFile(flashcard_img, filename='question.png')
    await callback.message.answer_photo(photo)
    await callback.message.answer(text='Do you know this word?', reply_markup=kb.known_unknown)

    

@router.callback_query(F.data == 'known')
async def rate_down(callback: CallbackQuery, state: FSMContext):
    cd = await state.get_data()
    new_rate_value = float(cd['current_cardset'][0][0])*0.75
    await rq.change_rate(current_language=cd['language'], word=cd['current_cardset'][0][1], new_val=new_rate_value)
    if await rq.check_if_need_transcr(cd['language']) == 't':
        flashcard_img = await repres.create_flashcard_t_answer(word=cd['current_cardset'][0][1], transcription=cd['current_cardset'][0][2], translation=cd['current_cardset'][0][3], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config=callback.data, c_lang=cd['language'])
        photo = BufferedInputFile(flashcard_img, filename='answer.png')
        await callback.message.answer_photo(photo)
        await callback.message.answer(text=f'Продолжить?', reply_markup=kb.continue_finish)
        
    elif await rq.check_if_need_transcr(cd['language']) == 'nt':
        flashcard_img = await repres.create_flashcard_t_answer(word=cd['current_cardset'][0][1], translation=cd['current_cardset'][0][2], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config=callback.data, c_lang=cd['language'])
        photo = BufferedInputFile(flashcard_img, filename='answer.png')
        await callback.message.answer_photo(photo)
        await callback.message.answer(text=f'Продолжить?', reply_markup=kb.continue_finish)


@router.callback_query(F.data == 'unknown')
async def rate_down(callback: CallbackQuery, state: FSMContext):
    cd = await state.get_data()
    if float(cd['current_cardset'][0][0])/0.75 >= 0:
        new_rate_value = float(cd['current_cardset'][0][0])
    else:
        new_rate_value = float(cd['current_cardset'][0][0])/0.75
    await rq.change_rate(current_language=cd['language'], word=cd['current_cardset'][0][1], new_val=new_rate_value)
    if await rq.check_if_need_transcr(cd['language']) == 't':
        flashcard_img = await repres.create_flashcard_t_answer(word=cd['current_cardset'][0][1], transcription=cd['current_cardset'][0][2], translation=cd['current_cardset'][0][3], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config=callback.data, c_lang=cd['language'])
        photo = BufferedInputFile(flashcard_img, filename='answer.png')
        await callback.message.answer_photo(photo)
        await callback.message.answer(text=f'Продолжить?', reply_markup=kb.continue_finish)

    
    elif await rq.check_if_need_transcr(cd['language']) == 'nt':
        flashcard_img = await repres.create_flashcard_t_answer(word=cd['current_cardset'][0][1], translation=cd['current_cardset'][0][2], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config=callback.data, c_lang=cd['language'])
        photo = BufferedInputFile(flashcard_img, filename='answer.png')
        await callback.message.answer_photo(photo)
        await callback.message.answer(text=f'Продолжить?', reply_markup=kb.continue_finish)


#---------TESTING_CARDS---------#

@router.message(Flow.mode, F.text.casefold() == 'тестик')
async def add_flashcard(message: Message, state: FSMContext):
    cd = await state.get_data()
    await state.update_data(mode=message.text)
    await state.set_state(Flow.card_test)
    await state.update_data(test_counter=0)
    await message.answer(text='Это режим теста! Можно выбрать, будешь ты переводить с иностранного на русский язык, или же наоборот, с русского на иностранный. Вводи свой ответ и проверяй знания! То слово, которое ты переведешь неверно будет чаще появляться для повторения.', reply_markup=ReplyKeyboardRemove())
    await message.answer(text='Выбери:', reply_markup=await kb.test_which_way(cd['language']))

@router.callback_query(F.data == 'foreign_rus')
async def foreign_rus(callback: CallbackQuery, state: FSMContext):
    cd = await state.get_data()
    cards = await rq.get_data_to_create_cards(cd['language'], cd['tg_id'])
    all_cards = [card[0:] for card in cards]
    if len(cards)<10:
        k_k=len(cards)
    else:
        k_k=10
    await state.update_data(test_wn=k_k)
    t_cs = random.sample(all_cards, k=k_k)
    await state.update_data(card_test='foreign_rus')
    await state.update_data(test_cardset=t_cs)
    await callback.message.edit_text(text='Начать тест?', reply_markup=kb.test_home_button)

@router.callback_query(F.data == 'rus_foreign')
async def foreign_rus(callback: CallbackQuery, state: FSMContext):
    cd = await state.get_data()
    cards = await rq.get_data_to_create_cards(cd['language'], cd['tg_id'])
    all_cards = [card[0:] for card in cards]
    print(all_cards)
    if len(cards)<10:
        k_k=len(cards)
    else:
        k_k=10
    await state.update_data(test_wn=k_k)
    t_cs = random.sample(all_cards, k=k_k)
    print(t_cs)
    await state.update_data(card_test='rus_foreign')
    await state.update_data(test_cardset=t_cs)
    await callback.message.edit_text(text='Начать тест?', reply_markup=kb.test_home_button)

@router.callback_query(F.data == 'testing')
async def question_st(callback: CallbackQuery, state:FSMContext):
    cd = await state.get_data()
    print(cd['test_cardset'])
    if cd['test_counter'] == cd['test_wn']:
        phrases = ["Главное не оценки, а знания!", "Я знаю только то, что ничего не знаю.", "Любая похвала будет тебя недооценивать", "Эй, умница! Называй меня Вяземским!"]
    else:
        phrases = ["Главное не оценки, а знания!", "Я знаю только то, что ничего не знаю.", "Любая похвала будет тебя недооценивать", "Не ошибается тот, кто не учится."]
    if cd['test_cardset'] == []:
        await callback.message.answer(text=f"Твой результат: {cd['test_counter']}/{cd['test_wn']} \n{random.choice(phrases)}", reply_markup=kb.finish_test)
    else:
        await state.set_state(Flow.test_answer)
        if cd['card_test'] == 'rus_foreign':
            if await rq.check_if_need_transcr(cd['language']) == 't':
                flashcard_img = await repres.create_flashcard_question(cd['test_cardset'][0][3], await rq.check_if_need_transcr(cd['language']), cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='question.png')
                await callback.message.answer_photo(photo)
            elif await rq.check_if_need_transcr(cd['language']) == 'nt':
                flashcard_img = await repres.create_flashcard_question(cd['test_cardset'][0][2], await rq.check_if_need_transcr(cd['language']), cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='question.png')
                await callback.message.answer_photo(photo)
        elif cd['card_test'] == 'foreign_rus':
            flashcard_img = await repres.create_flashcard_question(cd['test_cardset'][0][1], await rq.check_if_need_transcr(cd['language']), cd['language'])
            photo = BufferedInputFile(flashcard_img, filename='question.png')
            await callback.message.answer_photo(photo)

@router.message(Flow.test_answer)
async def answer_st(message: Message, state: FSMContext):
    cd = await state.get_data()
    await state.set_state(Flow.card_test)
    if await rq.check_if_need_transcr(cd['language']) == 't':
        current_card = [cd['test_cardset'][0][1], cd['test_cardset'][0][2], cd['test_cardset'][0][3]]
    elif await rq.check_if_need_transcr(cd['language']) == 'nt':
        current_card = [cd['test_cardset'][0][1], cd['test_cardset'][0][2]]
    cd['test_cardset'].pop(0)
    await state.update_data(test_cardset=cd['test_cardset'])
    cd = await state.get_data()
    print(cd['test_cardset'])
    if cd['card_test'] == 'rus_foreign':
        if current_card[0].casefold() == message.text:
            await state.update_data(test_counter=cd['test_counter']+1)
            if await rq.check_if_need_transcr(cd['language']) == 't':
                flashcard_img = await repres.create_flashcard_t_answer(word=current_card[0], transcription=current_card[1], translation=current_card[2], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config='correct', c_lang=cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='answer.png')
                await message.answer_photo(photo)
                await message.answer(text=f'Верно!', reply_markup = kb.continue_test)
            elif await rq.check_if_need_transcr(cd['language']) == 'nt':
                flashcard_img = await repres.create_flashcard_t_answer(word=current_card[0], translation=current_card[1], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config='correct', c_lang=cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='answer.png')
                await message.answer_photo(photo)
                await message.answer(text=f'Верно', reply_markup = kb.continue_test)
        else:
            if await rq.check_if_need_transcr(cd['language']) == 't':
                flashcard_img = await repres.create_flashcard_t_answer(word=current_card[0], transcription=current_card[1], translation=current_card[2], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config='wrong', c_lang=cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='answer.png')
                await message.answer_photo(photo)
                await message.answer(text=f'Неверно!', reply_markup = kb.continue_test)
            elif await rq.check_if_need_transcr(cd['language']) == 'nt':
                flashcard_img = await repres.create_flashcard_t_answer(word=current_card[0], translation=current_card[1], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config='wrong', c_lang=cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='answer.png')
                await message.answer_photo(photo)
                await message.answer(text=f'Неверно!', reply_markup = kb.continue_test)
    elif cd['card_test'] == 'foreign_rus':
        if await rq.check_if_need_transcr(cd['language']) == 't':
            if re.findall(f'.*{message.text.casefold()}.*', current_card[2].casefold()):
                await state.update_data(test_counter=cd['test_counter']+1)
                flashcard_img = await repres.create_flashcard_t_answer(word=current_card[0], transcription=current_card[1], translation=current_card[2], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config='correct', c_lang=cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='answer.png')
                await message.answer_photo(photo)
                await message.answer(text=f'Верно!', reply_markup = kb.continue_test)
            else:
                flashcard_img = await repres.create_flashcard_t_answer(word=current_card[0], transcription=current_card[1], translation=current_card[2], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config='wrong', c_lang=cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='answer.png')
                await message.answer_photo(photo)
                await message.answer(text=f'Неверно!', reply_markup = kb.continue_test)

        elif await rq.check_if_need_transcr(cd['language']) == 'nt':
            if re.findall(f'.*{message.text.casefold()}.*', current_card[1].casefold()):
                await state.update_data(test_counter=cd['test_counter']+1)
                flashcard_img = await repres.create_flashcard_t_answer(word=current_card[0], translation=current_card[1], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config='correct', c_lang=cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='answer.png')
                await message.answer_photo(photo)
                await message.answer(text=f'Верно', reply_markup = kb.continue_test)
            else:
                flashcard_img = await repres.create_flashcard_t_answer(word=current_card[0], translation=current_card[1], need_transcription=await rq.check_if_need_transcr(cd['language']), c_config='wrong', c_lang=cd['language'])
                photo = BufferedInputFile(flashcard_img, filename='answer.png')
                await message.answer_photo(photo)
                await message.answer(text=f'Неверно!', reply_markup = kb.continue_test)
       





#---------GLOBAL_UPDATES---------#


@router.message(Command('global_update'))
async def languages_update(message: Message):
    if str(message.from_user.id) == admin_id:
        await rq.update_language_list()

@router.message(Command('drop_table'))
async def drop_table(message: Message):
    if str(message.from_user.id) == admin_id:
        await rq.drop_tables()