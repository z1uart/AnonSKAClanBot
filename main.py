import json
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN, ADMIN_ID, MAINTENANCE_MODE
from logger import log_message, log_admin_reply

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# States
CHOOSING, SENDING_MESSAGE, ADMIN_REPLYING = range(3)

STATS_FILE = "user_stats.json"

CONFIG_FILE = "bot_config.json"

def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"maintenance_mode": False}

def set_config(maintenance_mode):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"maintenance_mode": maintenance_mode}, f)

def get_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error loading stats: {e}")
            return {}
    return {}

def update_stats(user_id):
    stats = get_stats()
    user_id_str = str(user_id)
    stats[user_id_str] = stats.get(user_id_str, 0) + 1
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f)
    except Exception as e:
        logger.error(f"Error saving stats: {e}")
    return stats[user_id_str]

# Keyboards
MAIN_MENU_KBD = [["Написать сообщение 🆕"], ["📊 Статистика", "❓ Помощь"]]
CANCEL_KBD = [["❌ Отмена"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return ConversationHandler.END

    config = get_config()
    if config.get("maintenance_mode") and update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ **Бот на техническом перерыве.**\n\nФункционал временно недоступен. Пожалуйста, попробуйте позже.", parse_mode="Markdown")
        return ConversationHandler.END

    text = (
        "👋 **Добро пожаловать!**\n\n"
        "Я — эксклюзивный бот для сообщества **SKA Clan**. Моя задача — быть вашим анонимным связным с администрацией канала.\n\n"
        "✨ Вы можете написать сообщение, и его моментально получит администратор. **Всё полностью анонимно.**\n\n"
        "👇 *Выберите действие:*"
    )
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KBD, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return CHOOSING

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    text = (
        "❓ **Помощь по боту**\n\n"
        "**Как это работает?**\n"
        "1. Нажмите **«Написать сообщение»**.\n"
        "2. Отправьте *любой* контент (текст, фото, видео и т.д.).\n"
        "3. Администратор получит ваше сообщение **без какой-либо информации о вас**.\n"
        "4. Если администратор решит ответить — вы получите его сообщение здесь.\n\n"
        "**Важно:**\n"
        "• Ваша личность **полностью скрыта**.\n"
        "• Администратор видит **только ваше сообщение**, без имён, ID или других данных.\n"
        "• Ответы приходят **только если администратор решит ответить**.\n"
        "• Сохраняйте уважительный тон общения."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user: return
    stats = get_stats()
    count = stats.get(str(update.effective_user.id), 0)
    await update.message.reply_text(f"📊 **Ваша статистика**\n\nВы отправили анонимных сообщений: `{count}`", parse_mode="Markdown")

async def request_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    text = (
        "📨 **Режим анонимной отправки**\n\n"
        "Вы можете отправить:\n"
        "• Текст 📝\n"
        "• Фото 🖼\n"
        "• Видео 🎬\n"
        "• Голосовое сообщение 🎤\n"
        "• Видеосообщение 🎥\n"
        "• Стикер ✨\n\n"
        "🚀 Ваше сообщение будет немедленно доставлено администратору.\n\n"
        "🛑 Чтобы отменить, нажмите кнопку «**Отмена**»."
    )
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(CANCEL_KBD, resize_keyboard=True),
        parse_mode="Markdown",
    )
    return SENDING_MESSAGE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    await update.message.reply_text(
        "❌ **Отправка отменена.**",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KBD, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return CHOOSING

async def handle_anonymous_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user: return
    user = update.effective_user
    msg = update.message
    
    content = ""
    msg_type = "text"
    
    if msg.text:
        content = msg.text
        msg_type = "text"
    elif msg.photo:
        content = f"Файл: {msg.photo[-1].file_id}"
        if msg.caption: content += f"\nПодпись: {msg.caption}"
        msg_type = "photo"
    elif msg.video:
        content = f"Файл: {msg.video.file_id}"
        if msg.caption: content += f"\nПодпись: {msg.caption}"
        msg_type = "video"
    elif msg.voice:
        content = f"Файл: {msg.voice.file_id}"
        msg_type = "voice"
    elif msg.video_note:
        content = f"Файл: {msg.video_note.file_id}"
        msg_type = "video_note"
    elif msg.sticker:
        content = f"Файл: {msg.sticker.file_id}"
        msg_type = "sticker"

    msg_id = log_message(user, msg_type, content)
    update_stats(user.id)
    
    # Forward to admin
    if ADMIN_ID != 0:
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("✉️ Ответить", callback_data=f"reply_to_{user.id}_{msg_id}")
        ]])
        
        if msg.text:
            admin_text = f"📩 **Анонимное сообщение**\n\n{msg.text}"
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown", reply_markup=reply_markup)
        else:
            admin_header = "📩 **Анонимное сообщение**"
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_header, parse_mode="Markdown")
            await msg.copy(chat_id=ADMIN_ID, reply_markup=reply_markup)
    
    await msg.reply_text(
        "✅ **Сообщение отправлено анонимно!**\n\nАдминистратор канала получил ваше сообщение.\nЕсли он решит ответить — вы получите уведомление здесь.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KBD, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return CHOOSING

async def admin_reply_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.from_user or query.from_user.id != ADMIN_ID:
        return
    
    await query.answer()
    if not query.data:
        return
    data = query.data.split("_")
    if len(data) < 4: return
    
    target_user_id = data[2]
    msg_id = data[3]
    
    if context.user_data is None:
        return
    context.user_data["reply_target"] = target_user_id
    context.user_data["reply_msg_id"] = msg_id
    
    if query.message:
        await query.message.reply_text(
            "Введите ваш ответ для анонимного пользователя:",
            reply_markup=ReplyKeyboardMarkup([["❌ Отменить ответ"]], resize_keyboard=True)
        )
    return ADMIN_REPLYING

async def process_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or update.effective_user.id != ADMIN_ID:
        return
    
    if context.user_data is None:
        return

    if update.message.text == "❌ Отменить ответ":
        context.user_data.pop("reply_target", None)
        context.user_data.pop("reply_msg_id", None)
        await update.message.reply_text(
            "❌ **Ответ отменен.**",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KBD, resize_keyboard=True),
            parse_mode="Markdown"
        )
        return CHOOSING

    target_user_id = context.user_data.get("reply_target")
    msg_id = context.user_data.get("reply_msg_id")
    
    if not target_user_id:
        await update.message.reply_text("❌ Ошибка: не найден получатель.")
        return CHOOSING

    # Content for logging
    log_content = update.message.text or (update.message.caption or "[Медиа]")

    try:
        target_user_id_int = int(target_user_id)
        logger.info(f"Attempting to send admin reply to user {target_user_id_int} for message {msg_id}")
        
        # Send reply as one message if it's text, otherwise keep existing logic for media
        if update.message.text:
            text = f"📨 **Ответ от администратора SKA Clan:**\n\n{update.message.text}"
            await context.bot.send_message(chat_id=target_user_id_int, text=text, parse_mode="Markdown")
        else:
            # For media, we still might need two messages or a caption
            if update.message.caption:
                caption = f"📨 **Ответ от администратора SKA Clan:**\n\n{update.message.caption}"
                await update.message.copy(chat_id=target_user_id_int, caption=caption, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=target_user_id_int, text="📨 **Ответ от администратора SKA Clan:**", parse_mode="Markdown")
                await update.message.copy(chat_id=target_user_id_int)
        
        log_admin_reply(target_user_id, msg_id, log_content)
        
        await update.message.reply_text(
            "✅ **Ответ успешно отправлен пользователю.**",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KBD, resize_keyboard=True),
            parse_mode="Markdown"
        )
        logger.info(f"Successfully sent reply to {target_user_id_int}")
    except Exception as e:
        logger.error(f"Error sending admin reply to {target_user_id}: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Ошибка при отправке: {e}")

    context.user_data.pop("reply_target", None)
    context.user_data.pop("reply_msg_id", None)
    return CHOOSING

async def admin_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or update.effective_user.id != ADMIN_ID: return
    if os.path.exists("anonymous_log.txt") and os.path.getsize("anonymous_log.txt") > 0:
        with open("anonymous_log.txt", "rb") as f:
            await update.message.reply_document(document=f, caption="📜 **Полный лог анонимных сообщений**", parse_mode="Markdown")
    else:
        await update.message.reply_text("📭 **Лог пока пуст.**", parse_mode="Markdown")

async def admin_log_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or update.effective_user.id != ADMIN_ID: return
    with open("anonymous_log.txt", "w") as f:
        f.write("")
    await update.message.reply_text("🗑 **Лог успешно очищен.**", parse_mode="Markdown")

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or update.effective_user.id != ADMIN_ID: return
    set_config(True)
    await update.message.reply_text("🛑 **Бот переведен в режим техобслуживания.**", parse_mode="Markdown")

async def start_bot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user or update.effective_user.id != ADMIN_ID: return
    set_config(False)
    await update.message.reply_text("🟢 **Бот выведен из режима техобслуживания.**", parse_mode="Markdown")

def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN is not set!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(admin_reply_button_handler, pattern="^reply_to_")
        ],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^Написать сообщение 🆕$"), request_message),
                MessageHandler(filters.Regex("^📊 Статистика$"), stats_command),
                MessageHandler(filters.Regex("^❓ Помощь$"), help_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, start),
            ],
            SENDING_MESSAGE: [
                MessageHandler(filters.Regex("^❌ Отмена$"), cancel),
                MessageHandler(filters.ALL & ~filters.COMMAND, handle_anonymous_message),
            ],
            ADMIN_REPLYING: [
                MessageHandler(filters.ALL & ~filters.COMMAND, process_admin_reply),
            ],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    # application.add_handler(CallbackQueryHandler(admin_reply_button_handler, pattern="^reply_to_"))
    application.add_handler(CommandHandler("adminlog", admin_log))
    application.add_handler(CommandHandler("adminlogclear", admin_log_clear))
    application.add_handler(CommandHandler("stopbot", stop_bot))
    application.add_handler(CommandHandler("startbot", start_bot_cmd))
    # application.add_handler(MessageHandler(filters.REPLY & filters.User(ADMIN_ID), admin_reply))

    # application.run_polling()
    import signal
    
    # Simple conflict handler - if we get conflict, we wait and try again or exit
    # to let the workflow manager restart us
    application.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    main()
