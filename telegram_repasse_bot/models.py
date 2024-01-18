from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from telegram_repasse_bot.database import db


class Base(DeclarativeBase):
    pass


class Forward(Base):
    __tablename__ = 'forwards'
    id: Mapped[int] = mapped_column(primary_key=True)
    from_chat: Mapped[str]
    to_chat: Mapped[str]


class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[int] = mapped_column(primary_key=True)
    from_message: Mapped[str]
    to_message: Mapped[str]
    to_chat: Mapped[str]


Base.metadata.create_all(db)
