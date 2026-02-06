from datetime import datetime
import os

LOG_FILE = "anonymous_log.txt"

def get_next_id():
    if not os.path.exists(LOG_FILE):
        return 1
    
    count = 0
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "[#" in line and "]" in line:
                count += 1
    return count + 1

def log_message(user, msg_type, content):
    msg_id = get_next_id()
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    username = f"@{user.username}" if user.username else "не указан"
    
    log_entry = (
        f"[#{msg_id}] ----------------------------------------------------------------------\n"
        f"👤 Имя: {first_name} {last_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 User ID: {user.id}\n"
        f"📅 Дата: {timestamp}\n"
        f"📨 Тип: {msg_type}\n"
        f"💬 Содержание:\n"
        f"{content}\n"
        f"----------------------------------------------------------------------\n"
    )
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    return msg_id

def log_admin_reply(user_id, msg_id, content):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    log_entry = (
        f"[Ответ на сообщение #{msg_id}]\n"
        f"👤 Админ ответил пользователю ID: {user_id}\n"
        f"📅 Дата: {timestamp}\n"
        f"💬 Ответ: {content}\n"
        f"----------------------------------------------------------------------\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
