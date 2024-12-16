from app.database.models import async_session
from app.database.models import User, Languages, Chinese_lib, English_lib, Base
from sqlalchemy import select, delete, update
from sqlalchemy.future import select

#---------REGISTRATION_REQUESTS---------#
async def check_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            return 'New'
            

async def get_user_name(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User.name).where(User.tg_id == tg_id))
        
        
async def set_user(tg_id, name):
    async with async_session() as session:
        session.add(User(tg_id=tg_id, name=name))
        await session.commit()
        
        

#---------BUTTONS_REQUESTS---------# 

async def get_languages():
    async with async_session() as session:
        return await session.scalars(select(Languages.lang))

async def my_languages(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User.languages).where(User.tg_id == tg_id))

async def list_lang(callbackdata,tg_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id==tg_id))
        row = result.scalar_one_or_none()

        if row:
            if row.languages==None:
                row.languages = f"{callbackdata}"
            else:
                if str(callbackdata) in str(row.languages).split(','):
                    pass
                else:
                    row.languages = f"{row.languages},{callbackdata}"
            await session.commit()
        
        else:
            print("Row not found")

async def edit_translation_rq(current_language:str, word: str, new_value: str):
    async with async_session() as session:
        async with session.begin():
            current_table= Base.metadata.tables[f"{current_language.casefold()}_lib"]
            upd_translation = (
                update(current_table)
                .where(current_table.c.word == word)
                .values(translation=new_value)
            )
            await session.execute(upd_translation)
            await session.commit()

async def change_rate(current_language:str, word: str, new_val: float):
    async with async_session() as session:
        async with session.begin():
            current_table= Base.metadata.tables[f"{current_language.casefold()}_lib"]
            upd_rate = (
                update(current_table)
                .where(current_table.c.word == word)
                .values(freq_rate=new_val)
            )
            await session.execute(upd_rate)
            await session.commit()



              


#---------CARDS_REQUESTS---------#

async def check_if_need_transcr(current_lang):
    async with async_session() as session:
        return await session.scalar(select(Languages.category).where(Languages.lang == current_lang))

async def add_new_card(tg_id, current_language, word, transcription, translation, rate):
    async with async_session() as session:
        current_table = Base.metadata.tables[f"{current_language.casefold()}_lib"]
        category = await session.scalar(select(Languages.category).where(Languages.lang == current_language))
        if category == 't':
            await session.execute(current_table.insert().values(tg_id=tg_id, word=word, transcription=transcription, translation=translation, freq_rate=rate))
            await session.commit()
        elif category == 'nt':
            await session.execute(current_table.insert().values(tg_id=tg_id, word=word, translation=translation, freq_rate=rate))
            await session.commit()

async def all_words_list(current_language):
    async with async_session() as session:
        current_table = Base.metadata.tables[f"{current_language.casefold()}_lib"]
        data = select(current_table.c.tg_id, current_table.c.word)
        result = await session.execute(data)
        rows = result.all()
        return rows

async def translation_data(current_language, current_word):
    async with async_session() as session:
        current_table = Base.metadata.tables[f"{current_language.casefold()}_lib"]
        return await session.scalar(select(current_table.c.translation).where(current_table.c.word == current_word))
        
async def get_data_to_create_cards(current_language, current_user):
    async with async_session() as session:
        current_table = Base.metadata.tables[f"{current_language.casefold()}_lib"]
        category = await session.scalar(select(Languages.category).where(Languages.lang == current_language))
        if category == 't':
            data = select(current_table.c.freq_rate, current_table.c.word, current_table.c.transcription, current_table.c.translation).where(current_table.c.tg_id == current_user)
            result = await session.execute(data)
            rows = result.all()
            return rows
        elif category == 'nt':
            data = select(current_table.c.freq_rate, current_table.c.word, current_table.c.translation).where(current_table.c.tg_id == current_user)
            result = await session.execute(data)
            rows = result.all()
            return rows

#---------GLOBAL UPDATES---------#

async def update_language_list():
    async with async_session() as session:
        session.add(Languages(lang='Español', category='nt'))
        await session.commit()


async def drop_tables():
    async with async_session() as session:
        table = Chinese_lib.__table__

        async with session.begin():
            connection = await session.connection()
            await connection.run_sync(table.drop)

