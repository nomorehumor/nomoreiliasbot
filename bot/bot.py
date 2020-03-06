import menu
import re
import enum
import telebot
import items
import sqlhandler
import config

if config.TOKEN is None:
    print("No BOT token found in environments variables")
    quit()

class ObjectTypes(enum.Enum):
    docs = "DOCS",
    links = "LINKS"


BOT = telebot.TeleBot(config.TOKEN)

@BOT.message_handler(commands=['start'])
def start(message):
    print(f'User connected @{message.from_user.username}')
    BOT.send_message(message.chat.id, "Hi, send document or link,"
                     + "or just forward it here")
    sqlhandler.save_user(message.chat.id)
    send_main_menu(message.chat.id)

@BOT.message_handler(commands=['docs'])
def get_docs_command(message=None, chat_id=None):
    """Docs command handling"""
    if message:
        send_folders_menu(message.chat.id, "DOCS", "📄")
    else:
        send_folders_menu(chat_id, "DOCS", "📄")

@BOT.message_handler(commands=['links'])
def get_links_command(message=None, chat_id=None):
    """Links command handling"""
    if message:
        send_folders_menu(message.chat.id, "LINKS", "🔗")
    else:
        send_folders_menu(chat_id, "LINKS", "🔗")


@BOT.message_handler(commands=["main_menu"])
def get_main_menu_command(message=None):
    send_main_menu(message.chat.id)

def send_main_menu(chat_id):
    BOT.send_message(chat_id, "*Choose the type to show:*",
                     reply_markup=menu.generate_start_menu(),
                     parse_mode='Markdown')

def send_folders_menu(chat_id, type, prefix):
    BOT.send_message(chat_id, prefix + " *Choose the folder:*",
                     reply_markup=menu.generate_folders_menu(type),
                     parse_mode='Markdown')


@BOT.message_handler(content_types=['document'])
def on_doc_receive(message):
    print("Received doc with id: " + str(message.document.file_id))
    doc_id = sqlhandler.save_doc(message.document.file_id,
                                 message.from_user.username)
    BOT.send_message(message.chat.id,
                 "⚠️ Warning, document was saved to the 'Common' folder⚠️ \n"
                   + "Please choose document's folder",
                    reply_markup=menu.generate_folders_menu("docs", doc_id))

@BOT.message_handler(content_types=["text"])
def on_link_received(message):
    """Checking whether incoming text is link and adding it to table"""
    print(message.text)
    link_pattern = re.compile(r"\b(https?|ftp|file)://[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#/%=~_|]")
    link = link_pattern.search(message.text)
    if link is not None:
        print('saving link')
        id = sqlhandler.save_link(link.group(0), message.from_user.username)
        BOT.send_message(message.chat.id,
                        "⚠️ Warning, link was saved to the 'Common' folder⚠️ \n"
                      + "Please choose link's folder",
                         reply_markup=menu.generate_folders_menu("links", id))
    else:
        print("no link found in text")

@BOT.callback_query_handler(func=lambda call: True)
def receive_answers(call):
    command = call.data.split("_")
    print(command)
    if len(command) == 1:
        # send folders for chosen type
        get_content_command = {
            'DOCS': get_docs_command,
            'LINKS': get_links_command
        }
        get_content_command[command[0]](chat_id=call.from_user.id)
    if len(command) == 2:
        # send items
        get_content = {
            'DOCS': send_docs,
            'LINKS': send_links
        }
        get_content[command[0]](call.from_user.id, command[1])
    elif len(command) == 3:
        # set folder of item
        result = sqlhandler.set_folder(command[0], command[1], command[2])
        if result:
            BOT.edit_message_text(chat_id=call.from_user.id,
                                  message_id=call.message.message_id,
                                  text="🎉 Folder successfully modified 🎉")
        send_main_menu(call.from_user.id)

    BOT.answer_callback_query(call.id, text="Loaded: ")

def send_docs(chat_id, folder):
    docs = sqlhandler.get_content('docs', folder)

    if not docs:
        BOT.send_message(chat_id,
                         "*" + folder + "*" + ": _No documents for now_",
                         parse_mode='Markdown')

    else:
        for doc in docs:
            BOT.send_document(chat_id,
                              doc.value,
                              caption="📄 *Folder:* "+ doc.folder +  "\n"
                               + "Posted by: @" + doc.user,
                              parse_mode='Markdown')
    send_main_menu(chat_id)


def send_links(chat_id, folder):
    links = sqlhandler.get_content('links', folder)
    if not links:
        BOT.send_message(chat_id, folder + ": _No links for now_",
                         parse_mode='Markdown')

    else:
        BOT.send_message(chat_id, "*Links:*", parse_mode='Markdown')
        for link in links:
            BOT.send_message(chat_id, "🔗 " + link.value + "\n"
                             + "*Folder:* " + link.folder + "\n\n"
                             + "*Posted by:* @" + link.user + "\n\n",
                             parse_mode="markdown")
    send_main_menu(chat_id)


@BOT.message_handler(commands=["broadcast"])
def broadcast_admin(message):
    text = message.text[10:]
    if message.from_user.username == "nomorehumor":
        broadcast(text)

def broadcast(text):
    users = sqlhandler.get_connected_users()
    for user in users:
        BOT.send_message(user[0], text)

BOT.polling(none_stop=True)
