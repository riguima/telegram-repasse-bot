from sqlalchemy import select
from telethon import TelegramClient, events

from bot import bot
from telegram_repasse_bot.config import get_config
from telegram_repasse_bot.database import Session
from telegram_repasse_bot.models import Forward, Message

client = TelegramClient(
    'anon', get_config()['api_id'], get_config()['api_hash']
)


@client.on(events.NewMessage)
async def forward_message(event):
    try:
        if get_config()['listen_ids']:
            user = await client.get_me()
            bot.send_message(
                user.id,
                f'{event.message.chat.title} - {event.message.chat.id}',
            )
    except AttributeError:
        pass
    with Session() as session:
        for forward in session.scalars(select(Forward)).all():
            if forward.from_chat == str(event.chat.id):
                message = await client.send_message(
                    int(forward.to_chat), event.message
                )
                session.add(
                    Message(
                        from_message=str(event.message.id),
                        to_message=str(message.id),
                        to_chat=forward.to_chat,
                    )
                )
                session.commit()


@client.on(events.MessageDeleted)
async def delete_message(event):
    with Session() as session:
        query = select(Message).where(
            Message.from_message == str(event.deleted_id)
        )
        message = session.scalars(query).first()
        if message:
            await client.delete_messages(
                entity=int(message.to_chat),
                message_ids=[int(message.to_message)],
            )


@client.on(events.MessageEdited)
async def edit_message(event):
    with Session() as session:
        query = select(Message).where(
            Message.from_message == str(event.message.id)
        )
        message = session.scalars(query).first()
        if message:
            await client.edit_message(
                entity=int(message.to_chat),
                message=int(message.to_message),
                text=event.message.text,
            )


if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()
