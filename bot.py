import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('./ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

PORT = int(os.environ.get('PORT', 5000))

STATE = 0

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = os.environ['API_key']

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update, context):
    global STATE
    if STATE != 1 and STATE != 2 and STATE != 3 and STATE != 4 and STATE != 5 and STATE != 6: 
        user_id = update.effective_chat.id
        id_ref = db.collection('Users').document(str(user_id))
        id_ref.set({'TelegramID' : int(user_id)})
        update.message.reply_text('Welcome to LEXANAS bot!\nUse /add to add a lesson\nUse /edit to edit a lesson information\nUse /remove to remove a lesson\nUse /list to view lesson\n\nNote: When adding lessons, avoid having lessons with the same name')
    else:
        update.message.reply_text('Invalid command! Input the lesson information first!')

def help(update, context):
    update.message.reply_text('Use /add to add a lesson\nUse /edit to edit a lesson information\nUse /remove to remove a lesson\nUse /list to view lesson\n\nNote: When adding lessons, avoid having lessons with the same name')

def add(update, context):
    global STATE
    if (STATE == 0):
        update.message.reply_text("What is the lesson name? Do try to be as specific as possible e.g. cs1010 lecture")
        STATE = 1

def edit(update, context):
    global STATE
    if (STATE == 0):
        update.message.reply_text("Which lesson would you like to edit?")
        STATE = 5


def remove(update, context):
    global STATE
    if (STATE == 0):
        update.message.reply_text("Which lesson would you like to remove?")
        STATE = 6

def get_mod(update, context):
    global STATE
    module = str(update.message.text)
    docus =  db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').stream()
    for docu in docus:
        if module == docu.to_dict()['Lesson name']:
            update.message.reply_text("You already have a lesson named " + module + "\n\nUse /help for more functions")
            STATE = 0
            return
    mod_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module)
    mod_ref.set({'Lesson name' : module, module : True})
    context.dispatcher.user_data['mod_name'] = module
    #update.message.reply_text("The lesson is: " + module)
    update.message.reply_text("What day is the lesson? Please indicate as a number, i.e. 1 for Monday, 2 for Tuesday, 7 for Sunday etc.")
    STATE = 2


def get_day(update, context):
    global STATE
    try:
        day = int(update.message.text)
        if (day >= 1) and (day <= 7):
            bool = True
        else:
            bool = False
    except ValueError:
        bool = False
    if bool:
        context.dispatcher.user_data['mod_day'] = day
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thurday", "Friday", "Saturday", "Sunday"]
        #update.message.reply_text("The day is: " + days_of_week[day-1])
        day_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(context.dispatcher.user_data['mod_name']).collection('LessonData').document(context.dispatcher.user_data['mod_name'] + ' day')
        day_ref.set({'Day' : day})
        update.message.reply_text("What time is the lesson? Please indicate as 24h time format, i.e. 0800 for 8am, 1330 for 1.30pm")
        STATE = 3
    else:
        update.message.reply_text("Invalid input! Please indicate the day of the lesson as a number, i.e. 1 for Monday, 2 for Tuesday, 7 for Sunday etc.")

def get_time(update, context):
    global STATE
    try:
        time = int(update.message.text)
        if (time % 100 <= 60) and (time >= 0) and (time <=2359):
            bool = True
        else:
            bool = False
    except ValueError:
        bool = False
    if bool:
        context.dispatcher.user_data['mod_time'] = time
        #update.message.reply_text("The time is: " + str(time))
        time_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(context.dispatcher.user_data['mod_name']).collection('LessonData').document(context.dispatcher.user_data['mod_name'] + ' time')
        time_ref.set({'Time' : time})
        update.message.reply_text("What is the zoom link/location of the lesson?")
        STATE = 4
    else:
        update.message.reply_text("Invalid input! Please indicate as 24h time format, i.e. 0800 for 8am, 1330 for 1.30pm")

def get_link(update,context):
    global STATE
    link = str(update.message.text)
    context.dispatcher.user_data['mod_link'] = link
    link_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(context.dispatcher.user_data['mod_name']).collection('LessonData').document(context.dispatcher.user_data['mod_name'] + ' link')
    link_ref.set({'Lesson Info' : link})
    time = context.dispatcher.user_data['mod_time']
    time_str = str(time)
    if (time < 100):
            time_str = '0' + str(time)
    if (time < 1000):
            time_str = '0' + time_str
    if (time < 10):
            time_str = '0' + time_str
    #update.message.reply_text("The lesson link/location is: " + link)
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thurday", "Friday", "Saturday", "Sunday"]
    update.message.reply_text("These are the details for the lesson:\nLesson: " + context.dispatcher.user_data['mod_name'] + "\nDay: " + days_of_week[context.dispatcher.user_data['mod_day'] - 1] + "\nTime: " + time_str + "\nLink/Location: " + context.dispatcher.user_data['mod_link'])
    update.message.reply_text("Use /help for more functions")
    STATE = 0

def edit_mod(update,context):
    global STATE
    module = str(update.message.text)
    #check if module = any module in database
    mod_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module)
    doc = mod_ref.get()
    if doc.exists:
        context.dispatcher.user_data['mod_name'] = module
        db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' day').delete()
        db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' time').delete()
        db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' link').delete()
        context.dispatcher.user_data['mod_day'] = None
        context.dispatcher.user_data['mod_time'] = None
        context.dispatcher.user_data['mod_link'] = None
        update.message.reply_text("What is the *NEW* day of the lesson? Please indicate as a number, i.e. 1 for Monday, 2 for Tuesday, 7 for Sunday etc.")
        STATE = 2
    else:
        update.message.reply_text("Could not find the lesson!\nUse /help for more functions")
        STATE = 0
    
def delete_mod(update,context):
    global STATE
    module = str(update.message.text)
    mod_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module)
    doc = mod_ref.get()
    if doc.exists:
        db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' day').delete()
        db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' time').delete()
        db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' link').delete()
        db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).delete()
        context.dispatcher.user_data['mod_name'] = None
        context.dispatcher.user_data['mod_day'] = None
        context.dispatcher.user_data['mod_time'] = None
        context.dispatcher.user_data['mod_link'] = None
        update.message.reply_text(module + " successfully deleted")
    else:
        update.message.reply_text("Could not find the lesson!\nUse /help for more functions")
    STATE = 0

def read(update, context):
    global STATE
    if STATE == 0:
        update.message.reply_text("Invalid command! Use /help for more functions")
    if STATE == 1:
        return get_mod(update, context)
    if STATE == 2:
        return get_day(update, context)
    if STATE == 3:
        return get_time(update,context)
    if STATE == 4:
        return get_link(update, context)
    if STATE == 5:
        return edit_mod(update, context)
    if STATE == 6:
        return delete_mod(update, context)

def list(update,context):
    array = []
    docus =  db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').stream()
    for docu in docus:
        array.append(docu.to_dict()['Lesson name'])
    if not array:
        update.message.reply_text("no modules added!")
    else:
        update.message.reply_text("These are the lessons you have added")
        for i in array:
            module = i
            day_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' day')
            time_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' time')
            link_ref = db.collection('Users').document(str(update.effective_chat.id)).collection('Lessons').document(module).collection('LessonData').document(module + ' link')
            day_doc = day_ref.get()
            time_doc = time_ref.get()
            link_doc = link_ref.get()
            day = day_doc.to_dict()['Day']
            time = time_doc.to_dict()['Time']
            link = link_doc.to_dict()['Lesson Info']
            time_str = str(time)
            if (time < 100):
                time_str = '0' + str(time)
            if (time < 1000):
                time_str = '0' + time_str
            if (time < 10):
                time_str = '0' + time_str
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thurday", "Friday", "Saturday", "Sunday"]
            update.message.reply_text("Lesson name: " + module + "\nLesson day: " + days_of_week[day-1] + "\nLesson time: " + time_str + "\nLink/Location: " + link)

# testing stuff
def get_id(update, context):
    id = str(update.effective_chat.id)
    update.message.reply_text("ID is : " + id)

def send(update, context):
    """
    if (context.dispatcher.user_data['mod_name']):
        update.message.reply_text("have input")
    else:
        update.message.reply_text("no input")
    """
    # id = 426487386 #jon
    id = -497653668  # group
    #id = 139551143 #yap
    #id = 620181594 #yx

    #for i in range (5):
    context.bot.send_message(chat_id=id, text="suck a dick")

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
    dp.add_handler(CommandHandler("list", list))

    # on noncommand
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
