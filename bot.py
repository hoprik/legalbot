import telebot
import logging
from yandex_gpt import PyYandexGpt
from database_YaGPT import Tokens
from database_history import History
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
dbt = Tokens("tokens.db")
dbh = History("history.db")
gpt = PyYandexGpt()
logging.basicConfig(level=logging.DEBUG)
dbt.create_tables()

system_prompt = "Ты - юрист, отвечай на проблемы пользователя статьями"

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    dbh.create_table(chat_id)
    dbt.create_user_profile(chat_id)
    bot.send_message(chat_id,
                     text=f"""
Привет, {user_name}! Я консультант по юр. проблемам, напиши свою проблему я ее прочитаю""")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                      text="""
Бот работает на базе YaGPT(ЯЖПТ)
База взята отсюда https://github.com/tecxz5/tg_plus_gpt""")


@bot.message_handler(commands=['clear'])
def clear(message):
    chat_id = message.chat.id
    dbh.clear_history(chat_id)
    bot.send_message(chat_id, "История отчищена")


@bot.message_handler(commands=['profile'])
def tokens_handler(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    tokens = dbt.get_tokens(chat_id)
    bot.send_message(chat_id, f"""Информация по пользователю {user_name}

Кол-во оставшихся токенов: {tokens}""")

@bot.message_handler(commands=['history'])
def history(message):
    try:
        history = dbh.get_history(message.chat.id, 10)
        if not history:
            history_message = "Нету истории"
        else:
            history_message = "\n".join([f"{row[0]}: {row[1]} (время: {row[2]})" for row in history])
        bot.send_message(message.chat.id, f"Вот ваша история:\n{history_message}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка при получении истории: {e}")

@bot.message_handler(content_types=['text'])
def text_reply(message):
    chat_id = message.chat.id
    current_tokens = dbt.get_tokens(chat_id)
    if current_tokens == 0:
        bot.send_message(chat_id,
                         "Ваши токены закончились, функция общения с нейросетью невозможна")
    else:
        text = message.text  # Получаем текст сообщения от пользователя
        user_history = dbh.get_history(message.chat.id, 3)
        history_text = "\n".join([f"{row[0]}: {row[1]} ({row[2]})" for row in user_history])
        logging.info(f"История общения: {history_text}")
        final_text = f"{text}, История чата: {history_text}"
        system_text = system_prompt
        prompt = [{"role": "system",
                   "text": system_text},
                  {"role": "user",
                   "text": final_text}]  # Используем текст сообщения как prompt
        response = gpt.create_request(chat_id, prompt)
        if response.status_code == 200:
            try:
                response_json = response.json()
                result_text = response_json['result']['alternatives'][0]['message']['text']
                logging.info(response_json)
                count = gpt.count_tokens(final_text)
                dbt.deduct_tokens(chat_id, count)
                bot.send_message(chat_id, result_text)
                dbh.save_message(chat_id, 'user', text)
                dbh.save_message(chat_id, 'assistant', result_text)
                logging.info(f"История ответа от пользователя {chat_id} сохранена")
                return
            except KeyError:
                logging.error('Ответ от API GPT не содержит ключа "result"')
                bot.send_message(chat_id, "Извините, не удалось сгенерировать историю.")
        else:
            logging.error(f'Ошибка API GPT: {response.status_code}')
            bot.send_message(chat_id, f"""
        Извините, произошла ошибка при обращении к API GPT.
        Ошибка: {response.status_code}
        Если ошибка 429 - нейросеть просит не так часто писать промпты либо же она нагружена""")
            return

@bot.message_handler(content_types=['voice'])
def voice_reply(message):
    bot.send_message('Это не тот проект')

if __name__ == "__main__":
    print("Бот запускается...")
    logging.info("Бот запускается...")
    bot.polling()