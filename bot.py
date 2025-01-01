from pathlib import Path

import toml
from sqlalchemy import select
from telebot import TeleBot
from telebot.util import quick_markup

from telegram_repasse_bot.config import get_config
from telegram_repasse_bot.database import Session
from telegram_repasse_bot.models import Forward, KeyWord

bot = TeleBot(get_config()['bot_token'])

from_chat = None


@bot.message_handler(commands=['parar_ids'])
def stop_show_ids(message):
    config = get_config()
    if config['listen_ids']:
        config['listen_ids'] = False
        toml.dump(config, open(Path('.config.toml').absolute(), 'w'))
        bot.send_message(message.chat.id, 'Parou de mostrar IDs')
        start(message)


@bot.message_handler(commands=['start', 'help'])
def start(message):
    if message.chat.username == get_config()['username']:
        bot.send_message(
            message.chat.id,
            'Escolha uma opção:',
            reply_markup=quick_markup(
                {
                    'Adicionar Repasse': {'callback_data': 'add_forward'},
                    'Remover Repasse': {'callback_data': 'remove_forward'},
                    'Listar Repasse': {'callback_data': 'show_forwards'},
                    'Adicionar Palavra Chave': {
                        'callback_data': 'add_keyword'
                    },
                    'Remover Palavra Chave': {
                        'callback_data': 'remove_keyword'
                    },
                    'Listar Palavras Chave': {
                        'callback_data': 'show_keywords'
                    },
                    'Mostrar IDs dos grupos/canais': {
                        'callback_data': 'listen_ids'
                    },
                }
            ),
        )


@bot.callback_query_handler(func=lambda c: c.data == 'add_forward')
def add_forward(callback_query):
    bot.send_message(
        callback_query.message.chat.id,
        'Digite o ID do grupo ou canal que vai pegar as mensagens:',
    )
    bot.register_next_step_handler(callback_query.message, on_from_chat)


def on_from_chat(message):
    global from_chat
    from_chat = message.text
    bot.send_message(
        message.chat.id,
        'Digite o ID do grupo ou canal onde vai ser repassado as mensagens:',
    )
    bot.register_next_step_handler(message, on_to_chat)


def on_to_chat(message):
    global from_chat
    with Session() as session:
        session.add(Forward(from_chat=from_chat, to_chat=message.text))
        session.commit()
    bot.send_message(message.chat.id, 'Repasse Adicionado')
    start(message)


@bot.callback_query_handler(func=lambda c: c.data == 'remove_forward')
def remove_forward(callback_query):
    reply_markup = {}
    with Session() as session:
        for forward in session.scalars(select(Forward)).all():
            reply_markup[f'{forward.from_chat} - {forward.to_chat}'] = {
                'callback_data': f'remove_forward:{forward.id}'
            }
    bot.send_message(
        callback_query.message.chat.id,
        'Escolha um repasse para ser removido:',
        reply_markup=quick_markup(reply_markup),
    )


@bot.callback_query_handler(func=lambda c: 'remove_forward:' in c.data)
def remove_forward_action(callback_query):
    forward_id = int(callback_query.data.split(':')[-1])
    with Session() as session:
        forward = session.get(Forward, forward_id)
        session.delete(forward)
        session.commit()
    bot.send_message(callback_query.message.chat.id, 'Repasse Removido')
    start(callback_query.message)


@bot.callback_query_handler(func=lambda c: c.data == 'show_forwards')
def show_forwards(callback_query):
    reply_markup = {}
    with Session() as session:
        for forward in session.scalars(select(Forward)).all():
            reply_markup[f'{forward.from_chat} - {forward.to_chat}'] = {
                'callback_data': f'show_forwards:{forward.id}'
            }
    bot.send_message(
        callback_query.message.chat.id,
        'Lista de Repasses',
        reply_markup=quick_markup(reply_markup),
    )
    start(callback_query.message)


@bot.callback_query_handler(func=lambda c: c.data == 'add_keyword')
def add_keyword(callback_query):
    bot.send_message(callback_query.message.chat.id, 'Digite a Palavra Chave:')
    bot.register_next_step_handler(callback_query.message, on_keyword)


def on_keyword(message):
    with Session() as session:
        session.add(KeyWord(value=message.text))
        session.commit()
    bot.send_message(message.chat.id, 'Palavra Chave Adicionada')
    start(message)


@bot.callback_query_handler(func=lambda c: c.data == 'remove_keyword')
def remove_keyword(callback_query):
    reply_markup = {}
    with Session() as session:
        for keyword in session.scalars(select(KeyWord)).all():
            reply_markup[keyword.value] = {
                'callback_data': f'remove_keyword:{keyword.id}'
            }
    bot.send_message(
        callback_query.message.chat.id,
        'Escolha uma Palavra Chave para ser removida:',
        reply_markup=quick_markup(reply_markup),
    )


@bot.callback_query_handler(func=lambda c: 'remove_keyword:' in c.data)
def remove_keyword_action(callback_query):
    keyword_id = int(callback_query.data.split(':')[-1])
    with Session() as session:
        keyword = session.get(KeyWord, keyword_id)
        session.delete(keyword)
        session.commit()
    bot.send_message(callback_query.message.chat.id, 'Palavra Chave Removida')
    start(callback_query.message)


@bot.callback_query_handler(func=lambda c: c.data == 'show_keywords')
def show_keywords(callback_query):
    reply_markup = {}
    with Session() as session:
        for keyword in session.scalars(select(KeyWord)).all():
            reply_markup[keyword.value] = {
                'callback_data': f'show_keywords:{keyword.id}'
            }
    bot.send_message(
        callback_query.message.chat.id,
        'Lista de Palavras Chave',
        reply_markup=quick_markup(reply_markup),
    )
    start(callback_query.message)


@bot.callback_query_handler(func=lambda c: c.data == 'listen_ids')
def start_listen_ids(callback_query):
    bot.send_message(
        callback_query.message.chat.id,
        'Começou a mostrar IDs de grupos e canais, para parar digite /parar_ids',
    )
    config = get_config()
    config['listen_ids'] = True
    toml.dump(config, open(Path('.config.toml').absolute(), 'w'))


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.infinity_polling()
