#   Binance Bot V1 - (Telegram Plugin)

# IMPORTS
#-------------------------------------------#
import time
import sqlite3

# pip install python-telegram-bot
from telegram.ext import Updater, CommandHandler

#-------------------------------------------#

# SETTINGS
#-------------------------------------------#
token = '' # TELEGRAM API KEY

#-------------------------------------------#

# FUNCTIONS
#-------------------------------------------#
# - BOT TIME
def bottime():
    bottime = time.strftime('%c')
    return bottime

# > MAIN
def main(token):
    updater = Updater(token=token,use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('open',open))
    dp.add_handler(CommandHandler('close',close))
    dp.add_handler(CommandHandler('status',status))
    dp.add_handler(CommandHandler('signals',signals))
    dp.add_handler(CommandHandler('lastprocess',lastProcess))
    dp.add_handler(CommandHandler('lastprocess2', lastProcess2))
    dp.add_handler(CommandHandler('lastprofitloss', lastprofitloss))
    dp.add_handler(CommandHandler('lastprofitloss2', lastprofitloss2))
    dp.add_handler(CommandHandler('help', help))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

# > OPEN
def open(update,context):
    database = sqlite3.connect('bot_log.sqlite')
    im = database.cursor()
    im.execute("UPDATE bot_status SET Status = 'Open', Time = '" + str(bottime()) + "' WHERE ID = '1'")
    database.commit()
    im.execute("SELECT * FROM bot_status WHERE ID = '1'")
    data = im.fetchall()
    database.close()
    update.message.reply_text('Bot is ' + str(data[0][1]) + 'ed - Last status time ' + str(data[0][2]))
# > OPEN
def close(update,context):
    database = sqlite3.connect('bot_log.sqlite')
    im = database.cursor()
    im.execute("UPDATE bot_status SET Status = 'Close', Time = '" + str(bottime()) + "' WHERE ID = '1'")
    database.commit()
    im.execute("SELECT * FROM bot_status WHERE ID = '1'")
    data = im.fetchall()
    database.close()
    update.message.reply_text('Bot is ' + str(data[0][1]) + 'd - Last status time ' + str(data[0][2]))
# > STATUS
def status(update,context):
    database = sqlite3.connect('bot_log.sqlite')
    im = database.cursor()
    im.execute("SELECT * FROM bot_status WHERE ID = '1'")
    data = im.fetchall()
    database.close()
    update.message.reply_text('Bot is ' + str(data[0][1]) + ' - Last status time ' + str(data[0][2]))
# > SIGNALS
def signals(update,context):
    database = sqlite3.connect('bot_log.sqlite')
    im = database.cursor()
    im.execute("SELECT * FROM bot_signals ORDER BY Time DESC")
    data = im.fetchall()
    database.close()
    update.message.reply_text('Signals data : ' + str(data[0][1]) + ' - Signals time :  ' + str(data[0][2]))
# > LAST PROFIT OR LOSS
def lastprofitloss(update, context):
    database = sqlite3.connect('bot_log.sqlite')
    im = database.cursor()
    im.execute("SELECT * FROM bot_profitloss ORDER BY ID DESC LIMIT 1")
    data = im.fetchall()
    database.close()
    if len(data) < 1:
        sendData = "Not enough data found."
    else:
        sendData = ("Pair :" + data[0][2] + ", Buy Price :" + data[0][3] + ", Sell Price :" + data[0][4] + ", Buy - Sell Count :" + data[0][5] + ", Buy RSI :" + data[0][6] + ", Sell RSI :" + data[0][7] + ", Profit or Loss :" + data[0][8] + ", Profit or Loss Rate :" + data[0][9] + ", Opening Time :" + data[0][10] + ", Closing Time :" + data[0][11])
    update.message.reply_text(sendData)
# > LAST PROFIT OR LOSS2
def lastprofitloss2(update, context):
    database = sqlite3.connect('bot_log.sqlite')
    im = database.cursor()
    im.execute("SELECT * FROM bot_profitloss ORDER BY ID DESC LIMIT 2")
    data = im.fetchall()
    database.close()
    if len(data) < 2:
        sendData = "Not enough data found."
    else:
        sendData = ("Pair :" + data[1][2] + ", Buy Price :" + data[1][3] + ", Sell Price :" + data[1][4] + ", Buy - Sell Count :" + data[1][5] + ", Buy RSI :" + data[1][6] + ", Sell RSI :" + data[1][7] + ", Profit or Loss :" + data[1][8] + ", Profit or Loss Rate :" + data[1][9] + ", Opening Time :" + data[1][10] + ", Closing Time :" + data[1][11])
    update.message.reply_text(sendData)
# > LAST PROCESS
def lastProcess(update, context):
    database = sqlite3.connect('bot_log.sqlite')
    im = database.cursor()
    im.execute("SELECT * FROM bot_logs ORDER BY Time DESC LIMIT 1")
    data = im.fetchall()
    database.close()
    if len(data) < 1:
        sendData = "Not enough data found."
    else:
        sendData = ("Process :" + data[0][0] + ", Pair :" + data[0][2] + ", Buy Price :" + data[0][3] + ", Sell Price :" + data[0][4] + ", Buy - Sell Count :" + data[0][5] + ", RSI :" + data[0][6] + ", Time :" + data[0][7])
    update.message.reply_text(sendData)

# > LAST PROCESS
def lastProcess2(update, context):
    database = sqlite3.connect('bot_log.sqlite')
    im = database.cursor()
    im.execute("SELECT * FROM bot_logs ORDER BY Time DESC LIMIT 2")
    data = im.fetchall()
    database.close()
    if len(data) < 2:
        sendData = "Not enough data found."
    else:
        sendData = ("Process :" + data[1][0] + ", Pair :" + data[1][2] + ", Buy Price :" + data[1][3] + ", Sell Price :" + data[1][4] + ", Buy - Sell Count :" + data[1][5] + ", RSI :" + data[1][6] + ", Time :" + data[0][7])
    update.message.reply_text(sendData)
# > HELP
def help(update, context):
    update.message.reply_text("Open Bot:/open - | - Close Bot:/close - | - Bot Status:/status - | - Last Pair Signals:/signals - | - Last Process:/lastprocess - | - Last Process2:/lastprocess2")

# > ERROR
def error(update,context):
    update.message.reply_text(f'Error! Adres:{context.error}')

#-------------------------------------------#


# TELEGRAM PLUGIN CODE
if __name__== "__main__":
    main(token)