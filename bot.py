from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json
import os
from datetime import datetime, timedelta

TOKEN = '8016153276:AAFlRHH4jCBkgRPPIPka2SjxY_QGYI6ZPxg'
ADMIN_ID = 1065790644
CHANNEL_LINK = 'https://t.me/ne_kit_a_tatoo'
PORTFOLIO_LINK = 'https://t.me/c/2651916205/14'
USERS_FILE = 'users.json'
POINTS_FILE = 'points.json'

FAQS = {
    "faq_care": (
        "Полная инструкция по уходу: https://t.me/ne_kit_a_tatoo/15\n"
        "1. Мойте руки перед касанием тату\n2. Мазь — только рекомендованные!\n"
        "3. Не сдирайте корки\n4. Не посещайте баню, бассейн 10 дней и т.д."
    ),
    "faq_heal": (
        "Заживление: от 10 до 21 дня. Всё зависит от ухода, зоны, особенностей кожи. "
        "Подробнее — https://t.me/ne_kit_a_tatoo/16"
    ),
    "faq_pain": (
        "Всё зависит от места и твоей чувствительности. Реально потерпеть даже новичкам. Есть обезболивание."
    ),
    "faq_price": (
        "Цена обсуждается индивидуально: зависит от размера, сложности, цвета. Примерные прайсы — https://t.me/ne_kit_a_tatoo/17"
    ),
    "faq_sport": (
        "Спорт, баня, сауна — не ранее чем через 10 дней после тату! Лучше 2 недели. Подробнее тут: https://t.me/ne_kit_a_tatoo/18"
    ),
}

def start(update, context):
    user_id = str(update.effective_user.id)
    args = context.args if hasattr(context, "args") else []
    referrer_id = None

    if args:
        referrer_id = args[0]
        if user_id != referrer_id:
            # Читаем базу пользователей
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    users = json.load(f)
            else:
                users = {}

            # Если пригласитель есть в базе
            if referrer_id in users:
                if "referrals" not in users[referrer_id]:
                    users[referrer_id]["referrals"] = []
                if user_id not in users[referrer_id]["referrals"]:
                    users[referrer_id]["referrals"].append(user_id)
                    # Добавляем баллы и в users.json
                    if "points" not in users[referrer_id]:
                        users[referrer_id]["points"] = 0
                    users[referrer_id]["points"] += 10

                    # Теперь добавляем баллы и в points.json!
                    if os.path.exists(POINTS_FILE):
                        with open(POINTS_FILE, 'r') as f:
                            points_data = json.load(f)
                    else:
                        points_data = {}
                    ref_points = points_data.get(referrer_id, {"points": 0, "last_roll": "", "streak": 0})
                    ref_points["points"] += 10
                    points_data[referrer_id] = ref_points
                    with open(POINTS_FILE, 'w') as f:
                        json.dump(points_data, f)
                    with open(USERS_FILE, 'w') as f:
                        json.dump(users, f)
                    try:
                        context.bot.send_message(
                            chat_id=int(referrer_id),
                            text=f"🔥 Ты пригласил друга! +10 баллов лояльности."
                        )
                    except Exception:
                        pass

    keyboard = [
        [InlineKeyboardButton("Вступить в канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✍️ Записаться на сеанс", callback_data='book_session')],
        [InlineKeyboardButton("Портфолио", url=PORTFOLIO_LINK)],
        [InlineKeyboardButton("Задать вопрос", callback_data='ask_question')],
        [InlineKeyboardButton("Обо мне", callback_data='about_me')],
        [InlineKeyboardButton("🎲 Кости / заработать баллы", callback_data='dice_game')],
        [InlineKeyboardButton("FAQ", callback_data='faq')],
        [InlineKeyboardButton("👥 Пригласить друга", callback_data='get_ref_link')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text(
            "👋 Привет! Ты на пути в мир тату, творчества!\n\n"
            "— Эксклюзивные эскизы\n— Советы по уходу\n— Запись на сеанс\n\n"
            "Выбери нужное ниже:",
            reply_markup=reply_markup
        )
    else:
        update.callback_query.message.reply_text(
            "👋 Привет! Ты на пути в мир тату, творчества!\n\n"
            "— Эксклюзивные эскизы\n— Советы по уходу\n— Запись на сеанс\n\n"
            "Выбери нужное ниже:",
            reply_markup=reply_markup
        )

def button(update, context):
    query = update.callback_query
    user_id = str(query.from_user.id)
    today = datetime.now().date().isoformat()
    points_data = {}

    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r") as f:
            try:
                points_data = json.load(f)
            except Exception:
                points_data = {}
    if isinstance(points_data.get(user_id), int):
        points_data[user_id] = {"points": points_data[user_id], "last_roll": "", "streak": 0}

    user_info = points_data.get(user_id, {"points": 0, "last_roll": "", "streak": 0})

    if query.data == 'ask_question':
        query.answer()
        query.message.reply_text("✍️ Напиши свой вопрос или заявку прямо сюда. Я лично отвечу тебе в ближайшее время!")

    elif query.data == 'about_me':
        query.answer()
        query.message.reply_text(
            "Привет 👋😊\n"
            "Ты здесь не случайно ✨\n"
            "Я вообще не верю в случайности 🔮\n\n"
            "Давай я просто расскажу немного о себе —\n"
            "а ты сам(а) решишь, остаться или нет 🙌\n\n"
            "Меня зовут Никита 💬\n"
            "Я люблю спорт 🥊, движение 🏃‍♂️ и дисциплину ⏱️\n"
            "С детства был непоседой 😅\n\n"
            "Постоянно думал кем же я хочу стать\n"
            "учился на повара 👨‍🍳, работал в разных местах 🧳\n"
            "Пробовал, искал, ошибался —\n"
            "и в итоге пришёл к тату 🖤\n\n"
            "А как именно я к этому пришёл? 🤫\n"
            "Это уже не для текста 🗣\n\n"
            "Выбирай эскиз, приходи на сеанс — и я расскажу 🎯\n"
            "Некоторые истории надо слышать вживую 🔥"
        )
    elif query.data == 'book_session':
        query.answer()
        context.user_data['booking'] = {}
        context.user_data['booking_step'] = 1
        query.message.reply_text("Как тебя зовут?")    

    elif query.data == 'dice_game':
        query.answer()
        # Бросаем кость через бота
        sent = query.message.reply_dice(emoji="🎲")
        # Дальше вызываем обработчик начисления баллов
        class DummyMessage:
            def __init__(self, message, dice):
                self.from_user = message.from_user
                self.dice = dice
                self.reply_text = message.reply_text
        dummy_update = type('obj', (object,), {'message': 
    DummyMessage(query.message, sent.dice)})()
        handle_dice(dummy_update, context)
    elif query.data == 'faq':
        query.answer()
        faq_keyboard = [
            [InlineKeyboardButton("🧴 Уход за тату", callback_data='faq_care')],
            [InlineKeyboardButton("⏳ Сколько заживает?", callback_data='faq_heal')],
            [InlineKeyboardButton("🤕 Больно ли?", callback_data='faq_pain')],
            [InlineKeyboardButton("💸 Сколько стоит?", callback_data='faq_price')],
            [InlineKeyboardButton("🏋️ Когда спорт?", callback_data='faq_sport')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_main')],
            [InlineKeyboardButton("👥 Пригласить друга", callback_data='get_ref_link')],
            [InlineKeyboardButton("✍️ Записаться на сеанс", callback_data='book_session')]
]
        query.message.reply_text(
            "Выбери интересующий вопрос:",
            reply_markup=InlineKeyboardMarkup(faq_keyboard)
        )

    elif query.data in FAQS:
        query.answer()
        query.message.reply_text(FAQS[query.data])
    elif query.data == 'get_ref_link':
        query.answer()
        user_id = str(query.from_user.id)
        bot_username = context.bot.username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        query.message.reply_text(
            f"Вот твоя персональная ссылка для друзей:\n\n{ref_link}\n\n"
            "Отправь другу! Когда он зайдёт — ты получишь +10 баллов и +лояльность 😉"
        )

    elif query.data == 'back_main':
        query.message.delete()
        start(update, context)

def handle_message(update, context):
    if update.message:
        user = update.message.from_user
        text = update.message.text
        save_user(user.id)
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❓ Новый вопрос от @{user.username or user.first_name} (ID: {user.id}):\n\n{text}"
        )
        update.message.reply_text("Спасибо за вопрос! Я отвечу тебе лично как можно скорее.")
    else:
        return  # если сообщение не текст — выходим без ошибки

def save_user(user_id):
    user_id = str(user_id)
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try:
                users = json.load(f)
            except Exception:
                users = {}
    else:
        users = {}

    if user_id not in users:
        users[user_id] = {"points": 0, "last_roll": "", "streak": 0, "referrals": []}

    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def handle_dice(update, context):
    user_id = str(update.message.from_user.id)
    today = datetime.now().date()
    points_file = POINTS_FILE

    if os.path.exists(points_file):
        with open(points_file, 'r') as f:
            try:
                points_data = json.load(f)
            except Exception:
                points_data = {}
    else:
        points_data = {}

    if isinstance(points_data.get(user_id), int):
        points_data[user_id] = {"points": points_data[user_id], "last_roll": "", "streak": 0}

    user_info = points_data.get(user_id, {"points": 0, "last_roll": "", "streak": 0})

    # Проверка последнего броска (и деление баллов, если не заходил)
    if user_info.get("last_roll"):
        last_roll_date = datetime.strptime(user_info["last_roll"], "%Y-%m-%d").date()
        delta_days = (today - last_roll_date).days
        if delta_days > 1:
            # Пропуск хотя бы одного дня — делим баллы пополам, сбрасываем серию
            user_info["points"] = user_info["points"] // 2
            user_info["streak"] = 1
            update.message.reply_text("Ты пропустил один или несколько дней — твои баллы уменьшены в 2 раза! Серия дней подряд сброшена.")
        elif delta_days == 1:
            user_info["streak"] += 1
        elif delta_days == 0:
            update.message.reply_text("Ты уже крутил кости сегодня! Приходи завтра.")
            return
        else:
            # Какая-то ошибка в датах, сбрасываем серию
            user_info["streak"] = 1
    else:
        user_info["streak"] = 1

    # Регистрируем бросок кости
    dice_value = update.message.dice.value
    points = dice_value * 2
    user_info["points"] += points
    user_info["last_roll"] = today.isoformat()

    points_data[user_id] = user_info

    with open(points_file, 'w') as f:
        json.dump(points_data, f)

    update.message.reply_text(
        f"Выпало: {dice_value}! Тебе начислено {points} баллов 🎉\n"
        f"Всего баллов: {user_info['points']}\n"
        f"Серия дней подряд: {user_info['streak']}"
    )

def my_progress(update, context):
    user_id = str(update.message.from_user.id)
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            points_data = json.load(f)
    else:
        points_data = {}
    user_info = points_data.get(user_id, {"points": 0, "last_roll": "", "streak": 0})

    # Если хочешь дополнительно показывать рефералов — тут можно добавить этот блок
    referrals_count = 0
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        user_full = users.get(user_id)
        if user_full and "referrals" in user_full:
            referrals_count = len(user_full["referrals"])

    text = (
        f"🔎 *Твой прогресс:*\n"
        f"Баллов: {user_info.get('points', 0)}\n"
        f"Последний бросок: {user_info.get('last_roll', '—')}\n"
        f"Серия дней подряд: {user_info.get('streak', 0)}\n"
        f"Друзей приглашено: {referrals_count}"
    )
    update.message.reply_text(text, parse_mode="Markdown")
def send_broadcast(update, context):
    # Только для администратора
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("⛔️ У тебя нет прав использовать эту команду.")
        return

    if not context.args:
        update.message.reply_text("Напиши текст рассылки после команды, например:\n/send Привет всем!")
        return

    message = ' '.join(context.args)

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    else:
        update.message.reply_text("Нет ни одного пользователя для рассылки.")
        return

    count = 0
    for user_id in users:
        try:
            context.bot.send_message(chat_id=user_id, text=message)
            count += 1
        except Exception:
            pass  # Игнорируем ошибки (например, если пользователь заблокировал бота)

    update.message.reply_text(f"Рассылка отправлена {count} пользователям.")
def show_top(update, context):
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            points_data = json.load(f)
    else:
        points_data = {}

    # Сортировка по баллам, ТОП 10
    top_users = sorted(points_data.items(), key=lambda x: x[1].get("points", 0), reverse=True)[:10]

    msg = "🏆 Топ-10 по баллам:\n"
    for i, (user_id, info) in enumerate(top_users, 1):
        msg += f"{i}. {user_id}: {info.get('points', 0)} баллов\n"

    update.message.reply_text(msg)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_booking))
    dp.add_handler(CommandHandler("myprogress", my_progress))
    dp.add_handler(CommandHandler("send", send_broadcast, pass_args=True))
    dp.add_handler(CommandHandler("top", show_top))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.dice, handle_dice))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    print('Бот запущен! Ожидаю команды в Telegram...')
    updater.start_polling()
    updater.idle()
def handle_booking(update, context):
    booking_steps = {
        1: ("name", "Сколько тебе лет?"),
        2: ("age", "Какой эскиз хочешь? (опиши или скинь ссылку)"),
        3: ("sketch", "Когда тебе удобно прийти на сеанс?"),
        4: ("datetime", "Твой номер телефона?"),
        5: ("phone", None)
    }

    step = context.user_data.get('booking_step', 0)
    if step == 0:
        return

    field, next_question = booking_steps[step]
    context.user_data['booking'][field] = update.message.text

    if next_question:
        context.user_data['booking_step'] += 1
        update.message.reply_text(next_question)
    else:
        booking_data = context.user_data['booking']
        booking_info = (
            f"🔔 *Новая заявка на сеанс!*\n\n"
            f"Имя: {booking_data['name']}\n"
            f"Возраст: {booking_data['age']}\n"
            f"Эскиз: {booking_data['sketch']}\n"
            f"Дата и время: {booking_data['datetime']}\n"
            f"Телефон: {booking_data['phone']}\n"
        )

        with open("bookings.txt", "a", encoding="utf-8") as f:
            f.write(booking_info + "\n" + "-"*30 + "\n")

        context.bot.send_message(chat_id=ADMIN_ID, text=booking_info, parse_mode="Markdown")
        update.message.reply_text("✅ Спасибо! Заявка отправлена. Скоро свяжусь с тобой.")
        context.user_data['booking_step'] = 0
        context.user_data['booking'] = {}
if __name__ == '__main__':
    
    main()
    input('нажми Enter...')