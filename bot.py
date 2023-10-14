from main import update_tokens, update_proxie, update_config, clear_status
import telebot

CHAT_ID = 450919685
bot = telebot.TeleBot('6640866974:AAHAoI71ZVaD_CK9dXC-XwVQUlaquyhj-Vw')
# user_states = {}

# def is_number(text):
#     try:
#         int(text)
#         return True
#     except ValueError:
#         return False

# @bot.message_handler(commands=['start'])
# def start(message):
#     markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1 = telebot.types.KeyboardButton("Очистить историю")
#     item2 = telebot.types.KeyboardButton("Проверить прокси")
#     item3 = telebot.types.KeyboardButton("Обновить токены")
#     item4 = telebot.types.KeyboardButton("Изменить интервал")
#     item5 = telebot.types.KeyboardButton("Изменить процент")
#     markup.add(item1, item2, item3, item4, item5)
    
#     bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)


# @bot.message_handler(func=lambda message: message.text == "Очистить историю")
# def clear_history(message):
#     clear_status()
#     bot.send_message(message.chat.id, "Успешно!")

# @bot.message_handler(func=lambda message: message.text == "Проверить прокси")
# def check_proxie(message):
#     bot.send_message(message.chat.id, f"Кол-во прокси: {update_proxie()}")

# @bot.message_handler(func=lambda message: message.text == "Обновить токены")
# def token_update(message):
#     bot.send_message(message.chat.id, f"Кол-во токенов: {update_tokens()}")

# @bot.message_handler(func=lambda message: message.text == "Изменить интервал")
# def change_interval(message):
#     user_states[message.chat.id] = "waiting_for_text_change_interval"
#     bot.send_message(message.chat.id, "Введите интервал целым числом минут\nВозможные значения 1,3,5,15,30,60,120,240,360,720")

# @bot.message_handler(func=lambda message: message.text == "Изменить процент")
# def change_percent(message):
#     user_states[message.chat.id] = "waiting_for_text_change_percent"
#     bot.send_message(message.chat.id, "Введите процент целым числом")

# @bot.message_handler(func=lambda message: message.chat.id in user_states and 
#                                   user_states[message.chat.id] in ["waiting_for_text_change_interval", "waiting_for_text_change_percent"])
# def handle_text(message):
#     user_state = user_states[message.chat.id]
#     text = message.text
#     if user_state == "waiting_for_text_change_interval":
#         if is_number(text):
#             interval = int(text)
#             if interval in [1,3,5,15,30,60,120,240,360,720]:
#                 bot.send_message(message.chat.id, f"Сохранено! Новые настройки: {update_config(['INTERVAL', interval])}")
#             else:
#                 bot.send_message(message.chat.id, f"Ошибка.")
#         else:
#             bot.send_message(message.chat.id, f"Ошибка.")
#     elif user_state == "waiting_for_text_change_percent":
#         if is_number(text):
#             percent = int(text)
#             bot.send_message(message.chat.id, f"Сохранено! Новые настройки: {update_config(['MIN_PERCENT', percent])}")
#         bot.send_message(message.chat.id, f"Ошибка.")

# def send_message_to_chat(chat_id, message):
#     bot.send_message(chat_id, message)

def get_bot_chats():
    chats = bot.get_updates()
    chat_ids = set()
    for chat in chats:
        chat_id = chat.message.chat.id
        chat_ids.add(chat_id)
    return chat_ids

print(get_bot_chats())
# bot.polling()