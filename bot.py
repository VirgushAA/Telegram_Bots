from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3


def create_db():
    con = sqlite3.connect('users.db')
    con.cursor().execute(''' CREATE TABLE IF NOT EXISTS users ( user_id INTEGER PRIMARY KEY,
                                                                score INTEGER DEFAULT 0 ) ''')
    con.commit()
    con.close()


async def register_user(user_id):
    con = sqlite3.connect('users.db')
    con.cursor().execute('INSERT OR IGNORE INTO users VALUES (?, ?)', (user_id, 0))
    con.commit()
    con.close()


async def show_score(update: Update, context: ContextTypes.DEFAULT_TYPE) ->None:
    user_id = update.effective_user.id
    con = sqlite3.connect('users.db')
    con.cursor().execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
    score = con.cursor().fetchone()
    if score:
        await update.message.reply_text(f'Твой текущий счет: {score[0]}!')
    else:
        await update.message.reply_text(f'Твой текущий счет: {0}!')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await register_user(user_id)
    await update.message.reply_text("Приветствую тебя в самом лучшем боте!")

if __name__ == "__main__":
    create_db()

    app = ApplicationBuilder().token("7634413552:AAEEDiyATQZEXVlpcOGI4-u7N0y1pMUt5hg").build()

    app.add_handler(CommandHandler('start', start))

    app.add_handler((CommandHandler('score', show_score)))

    app.run_polling()
