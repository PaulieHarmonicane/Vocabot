import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config.config import TOKEN
from app.handlers import router
from app.database.models import async_main

bot=Bot(token=TOKEN)
dp=Dispatcher()

async def main():
    await async_main()
    dp.include_router(router) 
    await dp.start_polling(bot)

if __name__ == '__main__': #makes it run only if we run this exact file, but not when it's imported
    #loprint (rq.get_languages())ssgging.basicConfig(level=logging.INFO) #use it only whileßß debugging``
    try:
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print ('Exit!')  #That's how we build the exception handlers


#TG buttons reply and inlinen