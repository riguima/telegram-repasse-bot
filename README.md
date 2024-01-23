# Telegram Repasse Bot

[![Presentation](https://99freelas.s3-sa-east-1.amazonaws.com/portfolios/imagens/original/1641617/54a30509-2025-4d15-b36a-a497bfc4f4f8/screenshot.png)](https://youtu.be/t4t2G9IBZgc)

Bot de repasse para Telegram, ele espelha mensagens de grupos, editando, excluindo e respondendo mensagens

## Instalação

Segue script de instalação:

```
git clone https://github.com/riguima/telegram-repasse-bot
cd telegram-repasse-bot
pip install -r requirements.txt
```

Renomeie o arquivo `.base.config.toml` para `.config.toml` e defina as seguintes váriaveis:

- `api_id` = API ID de sua conta do Telegram
- `api_hash` = API HASH de sua conta do Telegram
- `bot_token` = Token do bot criado no BotFather pelo Telegram
- `username` = nome de usuario da conta de Telegram que vai ter acesso ao bot
- `database_uri` = URL do banco de dados, exemplo com postgres: `postgresql://username:password@localhost:5432/database`

Rode com `python bot.py & python app.py`
