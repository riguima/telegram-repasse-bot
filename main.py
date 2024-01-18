from sqlalchemy import select
from telebot import TeleBot
from telebot.util import quick_markup

from telegram_repasse_bot.config import config
from telegram_repasse_bot.database import Session
from telegram_repasse_bot.models import Forward

bot = TeleBot(config['bot_token'])

from_chat = None


@bot.message_handler(commands=['start', 'help'])
def start(message):
    if message.chat.username == config['username']:
        bot.send_message(
            message.chat.id,
            'Escolha uma opção:',
            reply_markup=quick_markup(
                {
                    'Adicionar Repasse': {'callback_data': 'add_forward'},
                    'Remover Repasse': {'callback_data': 'remove_forward'},
                    'Listar Repasse': {'callback_data': 'show_forwards'},
                }
            ),
        )


@bot.callback_query_handler(func=lambda c: c.data == 'add_forward')
def add_forward(callback_query):
    bot.send_message(
        callback_query.message.chat.id,
        'Digite o ID/Título do grupo ou canal que vai pegar as mensagens:',
    )
    bot.register_next_step_handler(callback_query.message, on_from_chat)


def on_from_chat(message):
    global from_chat
    from_chat = message.text
    bot.send_message(
        message.chat.id,
        'Digite o ID/Título do grupo ou canal onde vai ser repassado as mensagens:',
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


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
    bot.infinity_polling()
