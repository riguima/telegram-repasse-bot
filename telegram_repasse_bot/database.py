from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from telegram_repasse_bot.config import get_config

db = create_engine(get_config()['database_uri'])
Session = sessionmaker(db)
