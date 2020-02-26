import telebot

def generate_inline_menu(buttons_and_callbacks=[]):
    keyboard = telebot.types.InlineKeyboardMarkup()

    for i in range(0, len(buttons_and_callbacks)):
        button = telebot.types.InlineKeyboardButton(text=buttons_and_callbacks[i][0],
                                                    callback_data=buttons_and_callbacks[i][1])
        keyboard.add(button)
    return keyboard


def generate_start_menu():
    buttons_and_callbacks = [("Show the documents 📄", "DOCS"),
                             ("Show the links 🔗", "LINKS")]
    return generate_inline_menu(buttons_and_callbacks)
    
def generate_folders_menu(type, id=""):
    if id != "":
        id = "_" + str(id)
    buttons_and_callbacks = [("GBI", type + id + "_GBI"),
                           ("HM I", type + id + "_HM"),
                           ("LA I", type + id + "_LA"),
                           ("Programmieren", type + id + "_PROG"),
                           ("Common", type + id + "_COMMON")]
    return generate_inline_menu(buttons_and_callbacks)

