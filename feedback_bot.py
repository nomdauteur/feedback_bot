import random
import os
import telebot
from systemd import journal
import mariadb
from datetime import datetime
import os


OWNER_CHAT_ID=-1002001493847

dir = os.path.dirname(__file__)
journal.write(os.environ['FB_TOKEN'])
TOKEN = os.environ['FB_TOKEN']
bot = telebot.TeleBot(TOKEN)

try:
    conn = mariadb.connect(
        user="wordlerbot",
        password="i4mp455w0rd_",
        host="localhost",
        database="bot_db"

    )
    journal.write(f"Connected well")
except mariadb.Error as e:
    journal.write(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

def send_help(chat_id):
    bot.send_message(chat_id,"Help's coming, now press /start to play more")    

# handlers


@bot.message_handler(commands=['help'])
def helper(message):
    send_help(message.chat.id)

@bot.message_handler(commands=['start', 'go'])

def start_handler(message):
    journal.write(message)
    chat_id = message.chat.id
    name=' '.join(filter(None, (message.chat.first_name, message.chat.last_name)))
    try:
        
        cur.execute(
    "INSERT INTO feedbackbot_users (id, name, last_visited, alias) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE last_visited=?", 
    (chat_id, name, datetime.now(), message.chat.username, datetime.now()) )
        conn.commit()
    except mariadb.Error as e:
        journal.write(f"Error in db: {e}")

    msg = bot.send_message(chat_id, 'Напишите свое сообщение:')

    bot.register_next_step_handler(msg, any_handler)

def any_handler(message):
    #journal.write(message)
    chat_id = message.chat.id
    if (message.text == '/help'):
        send_help(chat_id)
        return
    if (chat_id == OWNER_CHAT_ID):
        txt=message.text # /say 111 You're dick
        try:
            cmd, id, reply= txt.split(' ',2)
            if (cmd!='/say'):
                bot.send_message(OWNER_CHAT_ID, 'You probably fucked up the format2')
                return
            bot.send_message(id, reply)
            try:
        
                cur.execute(
    "INSERT INTO feedbackbot_convos (user_id, chat_id, is_msg_their, msg_date, msg_value, msg_id) VALUES (?, ?, ?, ?, ?, nextval(feedback_nums))", 
    (message.chat.username, id, 0, datetime.now(), reply) )
                conn.commit()
            except mariadb.Error as e:
                journal.write(f"Error in db: {e}")
            bot.send_message(OWNER_CHAT_ID, f'{id} получил "{reply}"')



        except Exception as e:
            bot.send_message(OWNER_CHAT_ID, 'You probably fucked up the format')
        return
    name=' '.join(filter(None, (message.chat.first_name, message.chat.last_name)))
    
    try:
        
        cur.execute(
    "INSERT INTO feedbackbot_convos (user_id, chat_id, is_msg_their, msg_date, msg_value, msg_id) VALUES (?, ?, ?, ?, ?, nextval(feedback_nums))", 
    (message.chat.username, chat_id, 1, datetime.now(), message.text) )
        conn.commit()
    except mariadb.Error as e:
        journal.write(f"Error in db: {e}")
    
    bot.send_message(OWNER_CHAT_ID, f'{chat_id} says {message.text}')

    msg = bot.send_message(chat_id, 'Ваше сообщение записано')

    bot.register_next_step_handler(msg, any_handler)


bot.polling(none_stop=True)