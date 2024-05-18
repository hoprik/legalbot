from typing import Optional
from dotenv import load_dotenv
import json, yandexapi, os, telebot
from telebot import types as tgtypes

bot = telebot.TeleBot(os.environ.get('TOKEN'))

def send_message(message: tgtypes.Message, text: str, keyboard: Optional[telebot.REPLY_MARKUP_TYPES]=None, edit_message=False) -> tgtypes.Message:
    if not edit_message:
        return bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)
    else:
        if type(keyboard) == tgtypes.InlineKeyboardMarkup:
            return bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id)
        else:
            raise TypeError("Invalid keyboard")

@bot.message_handler(commands=["start"])
def start(message: tgtypes.Message):
    send_message(message, "Привет, я бот помощник в сфере юристики. Спросить у меня можешь прописать комманду /ask. Так как наши услуги платные вы можете контролировать свои данные с помощь команды /profile")
    # если юзер не авторизирован в дб
    send_message(message, f"Внимание для использование этого бота нужно авторизоваться в системе hoprik auth. Для авторизации узнайте логин и пароль и нажмите кнопку авторизироватся",
                 tgtypes.ReplyKeyboardMarkup().add(tgtypes.KeyboardButton("Авторизироватся", web_app=tgtypes.WebAppInfo("https://hoprik.ru/auth/login"))))

@bot.message_handler(commands=["ask"])
def ask(message: tgtypes.Message):
    send_message(message, "Расскажи об ситуации")
    bot.register_next_step_handler(message, ask_handler)

@bot.message_handler(func=lambda message: False)
def ask_handler(message: tgtypes.Message):
    message_edit = send_message(message,"Нейросеть думает...", None, False)
    send_message(message_edit, "УК РФ Статья 228. Незаконные приобретение, хранение, перевозка, изготовление, переработка наркотических средств, психотропных веществ или их аналогов, а также незаконные приобретение, хранение, перевозка растений, содержащих наркотические средства или психотропные вещества, либо их частей, содержащих наркотические средства или психотропные вещества")

@bot.message_handler(commands=["profile"])
def ask(message: tgtypes.Message):
    send_message(message, "Токенов: хз, Голосовых блоков: хз")

bot.polling(none_stop=True)