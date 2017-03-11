#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This program is dedicated to the public domain under the CC0 license.
"""


from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ChatAction)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging, sqlite3, os, ConfigParser


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


WELCOME_STR = "Questo e il bot Telegram dell'Itis Cardano di Pavia.\nPer poter sfruttare al meglio le funzionalita offerte da questo bot, e' necessario rispondere alle seguenti domande:"
HELP_STR = "Per ricevere l'ultimo avviso pubblicato sul sito indirizzato alla tua classe digita il comando /avviso\nHai dei suggerimenti o vuoi saperne di piu' riguardo al progetto? Scrivi una mail a nutrialug@gmail.com con oggetto \"Cardano Telegram Bot\""

NOT_MANAGED_MSG_STR = "Comando o testo non riconosciuto"
CANCEL_STR = "Operazione annullata! Senza ultimare la procedura di profilazione potrai continuare ad utilizzare il bot, ma non potrai utilizzare molte delle sue funzionalita'. Per riavviare la procedura di profilazione digita il comando: /start"
SETTINGS_FILE_PATH = "./settings.ini"

BOT_CONFIG = {}
USERS_INFO = {}
YEAR, SECTION, COURSE, CONFIRM = range(4)

CUSTOM_KEYBOARD_YEAR = [["1", "2", "3"],["4", "5"]]
CUSTOM_KEYBOARD_SECTION = [["A", "B", "C"],["D", "E", "F"]]
CUSTOM_KEYBOARD_COURSE = [["Chimica", "Elettrotecnica"],["Informatica", "Liceo", "Meccanica"]]
CUSTOM_KEYBOARD_CONFIRM = [["Si", "No"]]


def setup_db_session():
    if os.path.isfile(BOT_CONFIG["db_file_path"]):
        return sqlite3.connect(BOT_CONFIG["db_file_path"])


def load_settings():
    """
    Load bot settings from .ini configuration file
    """
    config = ConfigParser.ConfigParser()
    config.read(SETTINGS_FILE_PATH)
    for item_key, item_value in config.items('main'):
        if item_value is not None:
            BOT_CONFIG[item_key] = item_value


# Define a few command handlers
def start(bot, update):
    """
    Start command handler
    Respond with the info about the bot and if user isn't yet registered initialize the profiling procedure
    """
    user_id = update.message.from_user.id

    conn = setup_db_session()
    c = conn.cursor()
    user = c.execute("SELECT year,section,course FROM users WHERE user_id=%s" % user_id).fetchone()

    if user is not None:
        # Existing user
        USERS_INFO[user_id] = {"user_id":user_id,"year":str(user[0]),"section":user[1].encode("utf-8"),"course":user[2].encode("utf-8")}
        print USERS_INFO[user_id]
        conn.close()
        bot.sendChatAction(user_id, action=ChatAction.TYPING)
        bot.sendMessage(user_id, "Bentornato " + update.message.from_user.first_name + "!")
        return ConversationHandler.END
    else:
        # New user
        conn.close()
        # save user_id
        USERS_INFO[user_id] = {"user_id":user_id}
        print USERS_INFO
        bot.sendChatAction(user_id, action=ChatAction.TYPING)
        bot.sendMessage(user_id, "Benvenuto " + update.message.from_user.first_name + "! " + WELCOME_STR)
        bot.sendChatAction(user_id, action=ChatAction.TYPING)
        bot.sendMessage(user_id, text="Per annullare la procedura di profilazione digita in qualsiasi momento il comando: /annulla")
        bot.sendChatAction(user_id, action=ChatAction.TYPING)
        bot.sendMessage(user_id, text="Le informazioni raccolte saranno trattate ed archiviate in forma totalmente anonima.")
        reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD_YEAR, one_time_keyboard=True)
        bot.sendChatAction(user_id, action=ChatAction.TYPING)
        bot.sendMessage(user_id, "Quale anno frequenti?", reply_markup=reply_markup)
        return YEAR


def help(bot, update):
    """
    Help command handler
    Respond with the help message about the bot functioning
    """
    user_id = update.message.from_user.id
    bot.sendChatAction(user_id, action=ChatAction.TYPING)
    bot.sendMessage(user_id, text=HELP_STR)


def unknown(bot, update):
    """
    Not covered messages types handler
    Respond with the
    """
    user_id = update.message.from_user.id
    bot.sendChatAction(user_id, action=ChatAction.TYPING)
    bot.sendMessage(user_id, text=NOT_MANAGED_MSG_STR)


def cancel(bot, update):
    """
    Cancel command handler
    """
    user_id = update.message.from_user.id
    reply_markup = ReplyKeyboardRemove()
    bot.sendChatAction(user_id, action=ChatAction.TYPING)
    bot.sendMessage(user_id, CANCEL_STR, reply_markup=reply_markup)
    # delete partialy collected user info
    USERS_INFO.pop(user_id)
    #print USERS_INFO
    return ConversationHandler.END


def get_year(bot, update):
    """
    Get and save user year property
    """
    user_id = update.message.from_user.id
    
    # save year
    USERS_INFO[user_id].update({"year":int(update.message.text)})
    #print USERS_INFO

    reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD_SECTION, one_time_keyboard=True)
    bot.sendChatAction(user_id, action=ChatAction.TYPING)
    bot.sendMessage(user_id, text="A quale sezione sei iscritto?", reply_markup=reply_markup)
    return SECTION


def get_section(bot, update):
    """
    Get and save user section property
    """
    user_id = update.message.from_user.id

    # save section
    USERS_INFO[user_id].update({"section":str(update.message.text)})
    #print USERS_INFO
    
    reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD_COURSE, one_time_keyboard=True)
    bot.sendChatAction(user_id, action=ChatAction.TYPING)
    bot.sendMessage(user_id, text="Di quale corso?", reply_markup=reply_markup)
    return COURSE


def get_course(bot, update):
    """
    Get and save user course property
    """
    user_id = update.message.from_user.id

    # save course
    USERS_INFO[user_id].update({"course":"C" if str(update.message.text) == "Chimica" else "E" if str(update.message.text) == "Elettrotecnica" else "M" if str(update.message.text) == "Meccanica" else "LS" if str(update.message.text) == "Liceo" else "I"})
    #print USERS_INFO
    
    bot.sendChatAction(user_id, action=ChatAction.TYPING)
    bot.sendMessage(user_id, text="Ecco il riepilogo dei dati da te inseriti")
    bot.sendChatAction(user_id, action=ChatAction.TYPING)
    bot.sendMessage(user_id, text="Anno : " + str(USERS_INFO[user_id]["year"]) + "\nSezione : " + USERS_INFO[user_id]["section"] + "\nCorso : " + update.message.text)    
    reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD_CONFIRM, one_time_keyboard=True)
    bot.sendChatAction(user_id, action=ChatAction.TYPING)
    bot.sendMessage(user_id, text="Sono corretti?", reply_markup=reply_markup)
    return CONFIRM


def confirm_profiling(bot, update):
    """
    Ask for confirmation of the correctness of inserted user info
    """
    user_id = update.message.from_user.id
    
    if update.message.text == "No":
        reply_markup = ReplyKeyboardRemove()
        bot.sendChatAction(user_id, action=ChatAction.TYPING)
        bot.sendMessage(user_id, CANCEL_STR, reply_markup=reply_markup)
        # delete partialy collected user info
        USERS_INFO.pop(user_id)
        #print USERS_INFO
        return ConversationHandler.END
    else:
        conn = setup_db_session()
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, year, section, course) VALUES (:user_id, :year, :section, :course)", USERS_INFO[user_id])
        conn.commit()
        conn.close()
        bot.sendChatAction(user_id, action=ChatAction.TYPING)
        bot.sendMessage(user_id, text="La profilazione è avvenuta con successo. Ora puoi iniziare ad utilizzare il bot al massimo delle sue possibilita'! Per maggiorni informazioni digita il comando: /help")
        return ConversationHandler.END


def get_last_notice_by_class(school_class):
    conn = setup_db_session()
    c = conn.cursor()
    notice = c.execute("SELECT number,path FROM notices WHERE classes LIKE " + "\"%" + school_class + "%\"").fetchone()
    notice_path = notice[1].encode("utf-8")
    return notice_path


def notice(bot, update):
    """
    Retrive the last notice associated to the user
    """
    user_id = update.message.from_user.id
    conn = setup_db_session()
    c = conn.cursor()
    user = c.execute("SELECT year,section,course FROM users WHERE user_id=%s" % user_id).fetchone()
    
    if user is not None:
        USERS_INFO[user_id] = {"user_id":user_id,"year":str(user[0]),"section":user[1].encode("utf-8"),"course":user[2].encode("utf-8")}
        school_class = str(USERS_INFO[user_id]["year"]) + USERS_INFO[user_id]["section"] + USERS_INFO[user_id]["course"]
        notice_pdf_file_path = get_last_notice_by_class(school_class)
        if os.path.isfile(notice_pdf_file_path):
            bot.sendChatAction(user_id, action=ChatAction.UPLOAD_DOCUMENT)
            notice = open(notice_pdf_file_path,'rb')
            bot.sendDocument(user_id,document=notice)
            notice.close()
        else:
            bot.sendChatAction(user_id, action=ChatAction.TYPING)
            bot.sendMessage(user_id, text="Si è verificato un errore durante il recupero dell'avviso")
    else:
        bot.sendChatAction(user_id, action=ChatAction.TYPING)
        bot.sendMessage(user_id, text="Non è possibile utilizzare questa funzionalità senza prima completare la registrazione. Per registrarti digita il comando /start e rispondi alle semplici domande.")
        

def error(bot, update, error):
    """
    Error handler
    Log the error on stdout
    """
    logger.warn('Update "%s" caused error "%s"' % (update, error))
    bot.sendChatAction(BOT_CONFIG["admin_user_id"], action=ChatAction.TYPING)
    bot.sendMessage(BOT_CONFIG["admin_user_id"], text='Update "%s" caused error "%s"' % (update, error))


def main():

    load_settings()
    
    # Create the EventHandler and pass it your bot's token
    updater = Updater(BOT_CONFIG['bot_token'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("avviso", notice))

    # Profiling handler
    profiling_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            YEAR: [RegexHandler('^(1|2|3|4|5)$', get_year)],
            SECTION: [RegexHandler('^(A|B|C|D|E|F|G|H|I|L|M|N|O|P|Q|R|S|T|U|V|Z)$', get_section)],
            COURSE: [RegexHandler('^(Chimica|Elettrotecnica|Informatica|Liceo|Meccanica)$', get_course)],
            CONFIRM: [RegexHandler('^(Si|No)$', confirm_profiling)]
        },
        fallbacks=[CommandHandler("annulla", cancel)]
    )

    dp.add_handler(profiling_handler)

    # On non known command and text messages
    dp.add_handler(MessageHandler(Filters.command, unknown))
    dp.add_handler(MessageHandler(Filters.text, unknown))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()


if __name__ == '__main__':
    main()
