import telebot
import items
import sqlhandler
import os
import menu
import re
import enum

token = os.environ['TEST_BOT_TOKEN']
if token is None:
    print("No bot token found in environments variables")
    quit()

class ObjectTypes(enum.Enum):
    docs = "DOCS",
    links = "LINKS"


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    print(f'User connected @{message.from_user.username}')
    bot.send_message(message.chat.id, "Привет, отправь документ или ссылку или просто перешли ее сюда")
    sqlhandler.save_user(message.chat.id)
    get_main_menu_command(message)


@bot.message_handler(commands=['docs'])
def get_docs_command(message = None, chat_id = None):
    """Docs command handling"""
    if message: 
        bot.send_message(message.chat.id, "*📄 Choose the folder:*", 
                    reply_markup=menu.generate_folders_menu("DOCS"), parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "*📄 Choose the folder:*", 
                     reply_markup=menu.generate_folders_menu("DOCS"), parse_mode='Markdown')

@bot.message_handler(commands=['links'])
def get_links_command(message = None, chat_id = None):
    """Links command handling"""
    if message:
        bot.send_message(message.chat.id, "*🔗 Choose the folder:*", 
                     reply_markup=menu.generate_folders_menu("LINKS"), parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "🔗 *Choose the folder:*", 
                     reply_markup=menu.generate_folders_menu("LINKS"), parse_mode='Markdown') 

@bot.message_handler(commands=["main_menu"])
def get_main_menu_command(message=None, chat_id=None):
    bot.send_message(message.chat.id, "Choose the folder:", reply_markup=menu.generate_start_menu())

@bot.message_handler(content_types=['document'])
def on_doc_receive(message):
    print("Received doc with id: " + str(message.document.file_id))
    id = sqlhandler.save_doc(message.document.file_id, message.from_user.username)                                        
    bot.send_message(message.chat.id, "⚠️ Warning, document was saved to the 'Common' folder⚠️ \n" 
                                          + "Please choose document's folder",
                                          reply_markup=menu.generate_folders_menu("docs", id)) 

@bot.message_handler(content_types=["text"])
def on_link_received(message):
    """Checking whether incoming text is link and adding it to table"""
    print(message.text)
    link_pattern = re.compile(r"\b(https?|ftp|file)://[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#/%=~_|]")
    link = link_pattern.search(message.text)
    if link is not None:
        print('saving link')
        id = sqlhandler.save_link(link.group(0), message.from_user.username)
        bot.send_message(message.chat.id, "⚠️ Warning, link was saved to the 'Common' folder⚠️ \n" 
                                          + "Please choose link's folder",
                                          reply_markup=menu.generate_folders_menu("links", id)) 
    else: 
        print("no link found in text")

@bot.callback_query_handler(func=lambda call: True)
def receive_answers(call):
    command = call.data.split("_")
    print(command)
    if len(command) == 1:
       get_content_command = {
            'DOCS': get_docs_command,
            'LINKS': get_links_command
       } 
       get_content_command[command[0]](chat_id=call.from_user.id)
    if len(command) == 2:
        """Sending docs"""
        get_content = {
            'DOCS': send_docs,
            'LINKS': send_links
        }
        get_content[command[0]](call.from_user.id, command[1])
    elif len(command) == 3:
        """Setting item's folder"""
        result = sqlhandler.set_folder(command[0], command[1], command[2])
        if result:
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="🎉 Folder successfully modified 🎉")
        get_main_menu_command(chat_id=call.from_user.id)

    bot.answer_callback_query(call.id, text="Loaded: ")
    


def send_docs(chat_id, folder):
    docs = sqlhandler.get_content('DOCS', folder)
    
    if not docs:
        bot.send_message(chat_id, "*" + folder + "*" + ": _No documents for now_", parse_mode='Markdown') 

    else: 
        for doc in docs:
            bot.send_document(chat_id, doc.value, caption="📄 *Folder:* "+ doc.folder +  "\n"
                                            + "Posted by: @" + doc.user, parse_mode='Markdown')
    bot.send_message(chat_id, "Choose the folder: ", reply_markup=menu.generate_start_menu())
    

def send_links(chat_id, folder):
    links = sqlhandler.get_content('LINKS', folder)
    if not links:
        bot.send_message(chat_id, folder + ": _No links for now_", parse_mode='Markdown')

    else:
        bot.send_message(chat_id, "*Links:*", parse_mode='Markdown')
        for link in links:
            bot.send_message(chat_id, "🔗 " + link.value + "\n"
                            + "**Folder:** " + link.folder + "\n\n"
                            + "**Posted by:** @" + link.user + "\n\n",
                            parse_mode="markdown")
    bot.send_message(chat_id, "Folders: ", reply_markup=menu.generate_start_menu())



@bot.message_handler(commands=["broadcast"])
def broadcast_admin(message):
    text = message.text[10:]
    if message.chat.id == 48712346:
        broadcast(text)

def broadcast(text):
    users = sqlhandler.get_connected_users()
    for user in users:
        bot.send_message(user[0], text)



bot.polling()
