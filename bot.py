from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import sqlite3


QUESTIONS = {
    'q1': { 'text': 'Что это на картинке?', 'image': 'images/xdd.jpeg', 'options': ['Кот', 'Собака', 'Лиса'], 'correct': 'Кот' },
    'q2': { 'text': 'Выбери правильный ответ.', 'image': 'images/math.jpg', 'options': ['2+2=3', '2+2=4', '2+2=5'], 'correct': '2+2=4' },
}


def create_db():
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute(''' CREATE TABLE IF NOT EXISTS users ( user_id INTEGER PRIMARY KEY,
                                                       username TEXT,
                                                       first_name TEXT,
                                                       score INTEGER DEFAULT 0 ) ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            user_id INTEGER,
            question_id TEXT,
            PRIMARY KEY (user_id, question_id)
        )
    ''')


    con.commit()
    con.close()


async def register_user(user: Update.effective_user):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    user_id = user.id
    user_name = user.username or ''
    first_name = user.first_name or ''
    # cur.execute('INSERT OR IGNORE INTO users VALUES (?, ?)', (user_id, 0))
    cur.execute('''
        INSERT INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name
    ''', (user_id, user_name, first_name))
    con.commit()
    con.close()


async def show_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
    score = cur.fetchone()
    if score:
        await update.message.reply_text(f'Твой текущий счет: {score[0]}!')
    else:
        await update.message.reply_text(f'Твой текущий счет: {0}!')


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT first_name, username, score FROM users ORDER BY score DESC')
    rows = cur.fetchall()
    con.close()

    if not rows:
        await update.message.reply_text("Пока нет участников. Ты будешь первым!")
        return

    leaderboard_text = "🏆 Таблица лидеров:\n\n"
    for idx, (first_name, username, score) in enumerate(rows, start=1):
        name = f"{first_name} (@{username})" if username else first_name
        leaderboard_text += f"{idx}. {name}: {score} баллов\n"

    await update.message.reply_text(leaderboard_text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await register_user(update.effective_user)
    if context.args:
        context.user_data['current_question'] = context.args[0]
        await handle_question_from_start(update, context)
    else:
        await update.message.reply_photo(photo=open('images/xdd.jpeg', 'rb'), caption='Приветствую тебя в самом лучшем боте!')


async def handle_question_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = QUESTIONS.get(context.user_data['current_question'])

    if not question:
        await update.message.reply_photo(photo=open('images/Vincent.jpg', 'rb'),
                                         caption='Такого вопроса нет. Не знаю как мы сюда попали.')
        return

    buttons = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in question['options']]
    keyboard = InlineKeyboardMarkup(buttons)

    if question.get('image'):
        with open(question['image'], 'rb') as img:
            await update.message.reply_photo(photo=img, caption=question['text'], reply_markup=keyboard)
    else:
        await update.message.reply_text(question['text'], reply_markup=keyboard)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_answer = query.data
    user_id = query.from_user.id
    question_id = context.user_data['current_question']

    if not question_id:
        with open('images/sadding.webp', 'rb') as img:
            await update.message.reply_photo(photo=img, caption='Мы в ошибке, я не знаю как.')
            return

    con = sqlite3.connect('users.db')
    cur = con.cursor()

    cur.execute('SELECT 1 FROM user_answers WHERE user_id = ? AND question_id = ?', (user_id, question_id))
    if cur.fetchone():
        await query.edit_message_caption('Ты уже отвечал на этот вопрос 😉')
        con.close()
        return

    correct_answer = QUESTIONS[question_id]['correct']

    if user_answer == correct_answer:
        cur.execute('UPDATE users SET score = score + 1 WHERE user_id = ?', (user_id,))
        response = 'И это правильный ответ, молодец. Вот тебе 1 балл.'
    else:
        response = f'А вот и нет, на самом деле ответ: {correct_answer}. Отнимать балл не будем.'

    cur.execute('INSERT INTO user_answers (user_id, question_id) VALUES (?, ?)', (user_id, question_id))
    con.commit()
    con.close()

    await query.edit_message_caption(response)

if __name__ == "__main__":
    create_db()

    app = ApplicationBuilder().token("7634413552:AAEEDiyATQZEXVlpcOGI4-u7N0y1pMUt5hg").build()

    app.add_handler(CommandHandler('start', start))

    app.add_handler((CommandHandler('score', show_score)))

    app.add_handler(CallbackQueryHandler(handle_answer))

    app.add_handler((CommandHandler('leaders', leaderboard)))

    # for cmd in QUESTIONS.keys():
    #     app.add_handler(CommandHandler(cmd, handle_question))
    for cmd in QUESTIONS.keys():
        app.add_handler(CommandHandler(cmd, handle_question_from_start))

    app.run_polling()
