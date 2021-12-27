from sqlite3.dbapi2 import connect
import Constant as keys
from telegram.ext import *
import Responses as R
from datetime import datetime
import sqlite3


print('MJClient Bot started...')

def connect_db():
    #Connecting DB
    connect = sqlite3.connect('customer.db')
    cursor = connect.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS customers(
        login TEXT PRIMARY KEY NOT NULL,
        amount INTEGER NOT NULL,
        credit FLOAT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        login TEXT NOT NULL,
        amount INTEGER,
        date INTEGER
    )""")

    return connect



def start_command(update, context):
    update.message.reply_text('Welcome to MJClient v1.0!!! Database connected! Lets GO!')


def help_command(update, context):
    update.message.reply_text('Поддерживаемые команды:\n' +
    '/add логин:str сумма:int\n' +
    'Добавляет транзакцию для логина с суммой, сумма может быть отрицательным числом\n' +
    '/list логин:str (количество:int)\n' +
    'Выводит список последних транзакций для логина, можно ввести количество\n' +
    '/all (количество:int)\n' +
    'Выводит список всех транзакций, можно ввести их количество\n' +
    '/user логин:str\n' +
    'Выводит общий долг пользователя с логином\n' +
    '/users (количество:int)\n' +
    'Выводит логины всех пользователей и их долги по убыванию, можно ввести их количество\n')

def add_command(update, context):
    connect = connect_db()
    cursor = connect.cursor()

    msg = update.message.text.split()
    customer = msg[1]
    amount = int(msg[2])
    date_added = update.message.date.strftime('%d %B %Y, %H:%M')

    cursor.execute("INSERT OR IGNORE INTO transactions(login, amount, date) VALUES(?, ?, ?)", (customer, amount, date_added, ))

    connect.commit()

    all_amount = cursor.execute("SELECT amount FROM transactions WHERE login=?", (customer, ))

    current_amount = 0

    for i in all_amount.fetchall():
        current_amount += i[0]


    print(current_amount)

    credit = 0

    cursor.execute("INSERT OR REPLACE INTO customers(login, amount, credit) VALUES(?, ?, ?)", (customer, current_amount, credit, ))

    connect.commit()


    reply = 'Добавлена транзакция для ' + customer + ' в размере ' + str(amount) + ' в ' + date_added + ' осталось всего: '
    reply += str(current_amount)

    update.message.reply_text(reply)

def list_command(update, context):
    connect = connect_db()
    cursor = connect.cursor()
    

    msg = update.message.text.split()
    customer = msg[1]
    if len(msg) < 3:
        count = 50
    else:
        count = int(msg[2])

    list_all = cursor.execute("SELECT login, amount, date FROM transactions WHERE login=? ORDER BY id DESC LIMIT ?", (customer, count, ))
    
    count = 0
    reply = '\n'

    for i in list_all.fetchall():
        count += 1
        reply = reply + '(' + str(i[1]) + ') в ' + i[2]
        reply += '\n'

    update.message.reply_text(f'Список последних {count} транзакций от {customer}: ' + reply)

def all_command(update, context):
    connect = connect_db()
    cursor = connect.cursor()
    

    msg = update.message.text.split()

    if len(msg) < 2:
        count = 50
    else:
        count = int(msg[1])

    list_all = cursor.execute("SELECT login, amount, date FROM transactions ORDER BY id DESC LIMIT ?", (count, ))
    
    count = 0
    reply = '\n'
    for i in list_all.fetchall():
        count += 1
        reply = reply + i[0] + '(' + str(i[1]) + ') в ' + i[2]
        reply += '\n'

    update.message.reply_text(f'Список последних {count} транзакций: ' + reply)


def users_command(update, context):
    connect = connect_db()
    cursor = connect.cursor()
    
    msg = update.message.text.split()

    if len(msg) < 2:
        count = 30
    else:
        count = int(msg[1])

    users_list = cursor.execute("SELECT login, amount FROM customers ORDER BY amount DESC LIMIT ?", (count, ))
    
    count = 0
    reply = '\n'
    for i in users_list.fetchall():
        count += 1
        reply = reply + i[0] + ' имеет долг: ' + str(i[1])
        reply += '\n'

    update.message.reply_text(f'Список последних {count} пользователей по величине долга: ' + reply)

def user_command(update, context):
    connect = connect_db()
    cursor = connect.cursor()
    
    msg = update.message.text.split()
    customer = msg[1]

    users_list = cursor.execute("SELECT amount FROM customers WHERE login=?", (customer, )) 

    update.message.reply_text(f'Пользователь с логином {customer} имеет долг: ' + str(users_list.fetchall()[0][0]))


def handle_message(update, context):
    text = str(update.message.text).lower()
    response = R.sample_responses(text)

    update.message.reply_text(response)


def error(update, context):
    print(f"Upgrade {update} caused error {context.error}")


def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('add', add_command))
    dp.add_handler(CommandHandler('list', list_command))
    dp.add_handler(CommandHandler('all', all_command))
    dp.add_handler(CommandHandler('users', users_command))
    dp.add_handler(CommandHandler('user', user_command))

    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling(1)
    updater.idle()


if __name__ == '__main__':
    main()