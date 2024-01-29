#-*- coding: utf-8 -*-
from configparser import ConfigParser
from aiogram import Bot, Dispatcher, executor, types

from src.brain import Brain

from src.utils.sugar import datetime
import time, gc, os, sys


ROOT = os.path.dirname(sys.argv[0])
ROOT and os.chdir(ROOT)

CONFIG_FILE_PATH = './config.ini'

def init_handlers(dp, confdad):
    brain = Brain(confdad.get('BOT', 'brain_dir_path'))

    @dp.message_handler(commands=['start'])
    async def start_bot(msg: types.Message):
        await msg.answer(text=confdad.get('CMD', 'start'))

    @dp.message_handler(commands=['help'])
    async def send_help_text(msg: types.Message):
        if confdad.getboolean('BOT', 'send_to_user'):
            await dp.bot.send_message(chat_id=msg.from_user.id, text=confdad.get('CMD', 'help'))
            return

        await dp.bot.send_message(chat_id=msg.chat.id, text=confdad.get('CMD', 'help'))
        await msg.delete()

    @dp.message_handler(content_types=['new_chat_members'])
    async def new_chat_members(msg:types.Message):
        await dp.bot.send_message(chat_id=msg.chat.id, text=confdad.get('BOT', 'new_group_text'))
    @dp.message_handler()
    async def check_all_messages(msg: types.Message):
        # если сообщение является ответом на сообщение, то обучаем бота
        if msg.reply_to_message:
            await brain.train(msg.chat.id, msg.reply_to_message.text, msg.text)

        bot_answer = await brain.answer(msg.chat.id, msg.text)
        if bot_answer:
            await msg.reply(bot_answer)

def main():
    confdad = ConfigParser()
    if not confdad.read(CONFIG_FILE_PATH, encoding='utf-8'):
        raise Exception(f'"{CONFIG_FILE_PATH}" not found')

    try:
        bot = Bot(confdad.get('BOT', 'token'))
        dp = Dispatcher(bot)

        init_handlers(dp, confdad)
        executor.start_polling(dp, skip_updates=confdad.get('BOT', 'skip_updates'))
    except Exception as e:
        e_message = f'[{datetime()}][unhandled]: {e}'

        with open('error.log', 'a', encoding='utf-8') as f:
            f.write(f'{e_message}\n')

        print(f'\n{e_message}')
        gc.collect()

        time.sleep(confdad.getint('BOT', 'restart_timeout_sec'))
        main()

if __name__ == '__main__':
    main()
