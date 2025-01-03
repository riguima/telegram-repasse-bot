import os

from sqlalchemy import select
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import ChatForwardsRestrictedError

from bot import bot
from telegram_repasse_bot.config import get_config
from telegram_repasse_bot.database import Session
from telegram_repasse_bot.models import Forward, KeyWord, Message

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
        for keyword in session.scalars(select(KeyWord)).all():
            if keyword.value.lower() in event.raw_text.lower():
                return
        for forward in session.scalars(select(Forward)).all():
            if forward.from_chat == str(event.chat.id):
                if event.message.reply_to:
                    with Session() as session:
                        query = select(Message).where(
                            Message.from_message
                            == str(event.message.reply_to.reply_to_msg_id)
                        )
                        replied_message = session.scalars(query).first()
                        try:
                            message = await client.send_message(
                                int(forward.to_chat),
                                event.message,
                                reply_to=int(replied_message.to_message),
                            )
                        except ChatForwardsRestrictedError:
                            path = await event.message.download_media()
                            message = await client.send_file(
                                int(forward.to_chat),
                                path,
                                caption=event.message.text,
                                reply_to=int(replied_message.to_message),
                            )
                            os.remove(path)
                else:
                    try:
                        message = await client.send_message(
                            int(forward.to_chat), event.message
                        )
                    except ChatForwardsRestrictedError:
                        path = await event.message.download_media()
                        message = await client.send_file(
                            int(forward.to_chat),
                            path,
                            caption=event.message.text,
                        )
                        os.remove(path)
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
