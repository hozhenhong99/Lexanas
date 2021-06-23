import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import time
PORT = int(os.environ.get('PORT', 5000))

STATE = 0

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '1780794178:AAEFUP4qL57yJiRvora8C4LNS-JufkSsLpY'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    update.message.reply_text(
        'Welcome to LEXANAS bot!\nUse /add to add a module\nUse /edit to edit a module information\nUse /remove to remove a module')

def help(update, context):
    update.message.reply_text(
        'Use /add to add a module\nUse /edit to edit a module information\nUse /remove to remove a module')

def add(update, context):
    global STATE
    update.message.reply_text("What is the module code?")
    STATE = 1

def edit(update, context):
    update.message.reply_text("Which module would you like to edit?")

def remove(update, context):
    update.message.reply_text("Which module would you like to remove?")

def get_mod(update, context):
    global STATE
    module = str(update.message.text)
    context.dispatcher.user_data['mod_name'] = module
    update.message.reply_text("The module is: " + module)
    update.message.reply_text("What day is the lesson? Please indicate as a number, i.e. 1 for Monday, 2 for Tuesday, 7 for Sunday etc.")
    STATE = 2


def get_day(update, context):
    global STATE
    #update.message.reply_text("test")
    try:
        day = int(update.message.text)
        bool = True
    except ValueError:
        bool = False
    if ((bool) and (day >= 1) and (day <= 7)):
        context.dispatcher.user_data['mod_day'] = day
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thurday", "Friday", "Saturday", "Sunday"]
        update.message.reply_text("The day is: " + days_of_week[day-1])
        update.message.reply_text("What time is the lesson? Please indicate as 24h time format, i.e. 0800 for 8am, 1330 for 1.30pm")
        STATE = 3
    else:
        update.message.reply_text("Invalid input! Please indicate the day of the lesson as a number, i.e. 1 for Monday, 2 for Tuesday, 7 for Sunday etc.")

def get_time(update, context):
    global STATE
    try:
        time = int(update.message.text)
        bool = True
    except ValueError:
        #update.message.reply_text("Invalid input! Please indicate as 24h time format i.e. 0800 for 8am, 1330 for 1.30pm")
        bool = False
    if bool:
        context.dispatcher.user_data['mod_time'] = time
        update.message.reply_text("The time is: " + str(time))
        update.message.reply_text("What is the zoom link/location of the lesson?")
        STATE = 4
    else:
        update.message.reply_text("Invalid input! Please indicate as 24h time format, i.e. 0800 for 8am, 1330 for 1.30pm")

def get_link(update,context):
    global STATE
    link = str(update.message.text)
    context.dispatcher.user_data['mod_link'] = link
    update.message.reply_text("The module link/location is: " + link)

def read(update, context):
    global STATE
    if STATE == 1:
        return get_mod(update, context)
    if STATE == 2:
        return get_day(update, context)
    if STATE == 3:
        return get_time(update,context)
    if STATE == 4:
        return get_link(update, context)

def list_mod(update,context):
    update.message.reply_text("Module: " + context.dispatcher.user_data['mod_name'] + "\nDay: " + str(context.dispatcher.user_data['mod_day']) + "\ntime: " + str(context.dispatcher.user_data['mod_time']) + "\nLink/Location: " + context.dispatcher.user_data['mod_link'])

# testing stuff
def get_id(update, context):
    id = str(update.effective_chat.id)
    update.message.reply_text("ID is : " + id)

def send(update, context):
    # id = 426487386 #jon
    id = -497653668  # group
    # for i in range (5):
    context.bot.send_message(chat_id=id, text="fk u")


def fkjon(update, context):
    update.message.reply_text("fk u jon!")
    update.message.reply_text(
        "/fk_jon@lexanas_bot\n/fk_yx@lexanas_bot\n/fk_yap@lexanas_bot\n/fk_jim@lexanas_bot")


def fkyx(update, context):
    update.message.reply_text("fk u yx!")
    update.message.reply_text(
        "/fk_jon@lexanas_bot\n/fk_yx@lexanas_bot\n/fk_yap@lexanas_bot\n/fk_jim@lexanas_bot")


def fkyap(update, context):
    update.message.reply_text("fk u yap!")
    update.message.reply_text(
        "/fk_jon@lexanas_bot\n/fk_yx@lexanas_bot\n/fk_yap@lexanas_bot\n/fk_jim@lexanas_bot")


def fkjim(update, context):
    update.message.reply_text("fk u jim!")
    update.message.reply_text(
        "/fk_jon@lexanas_bot\n/fk_yx@lexanas_bot\n/fk_yap@lexanas_bot\n/fk_jim@lexanas_bot")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("edit", edit))
    dp.add_handler(CommandHandler("remove", remove))

    # testing
    dp.add_handler(CommandHandler("get_id", get_id))
    dp.add_handler(CommandHandler("send", send))
    dp.add_handler(CommandHandler("list", list_mod))

    # dumb stuff
    dp.add_handler(CommandHandler("fk_jon", fkjon))
    dp.add_handler(CommandHandler("fk_yx", fkyx))
    dp.add_handler(CommandHandler("fk_yap", fkyap))
    dp.add_handler(CommandHandler("fk_jim", fkjim))

    # log all errors
    dp.add_error_handler(error)

    # on noncommand i.e message - read the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, read))

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url='https://lexanasbot.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
