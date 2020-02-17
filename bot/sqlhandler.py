import items
import pymysql

conn = pymysql.connect(user='root', password='Theye0011' ,database='docs', host='localhost')

def save_user(chat_id):
    if not check_user_connected(chat_id):
        with conn:
            cursor = conn.cursor()
            cursor.execute(f'insert into connected_users (chat_id) values ({chat_id})')
            print(f"Added user with chat_id = {chat_id} to table")
            conn.commit()
            cursor.close()

def check_user_connected(chat_id):
    is_user_in_table = False
    with conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM connected_users WHERE chat_id=({chat_id})')
        if cursor.fetchall():
            is_user_in_table = True
            print(f'user with chat id {chat_id} has connected previously')
    return is_user_in_table


def get_connected_users():
    users = []
    with conn:
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM connected_users')
        users = cursor.fetchall()
    return users

def save_doc(value, username):
    id = 0
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO docs (value, linkedUser, folder) VALUES ('{value}', '{username}', 'COMMON');" +
                        "SELECT LAST_INSERT_ID();")
        output = cursor.fetchall()
        id = output[0][0]
    return id
    
def save_link(value, username):
    id = 0
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO links (value, linkeduser, folder) VALUES ('{value}', '{username}', 'COMMON')" +
                        "SELECT LAST_INSERT_ID();")
        output = cursor.fetchall()
        id = output[0][0]
    return id


def get_content(type, folder):
    content = []
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"select * from {type} where folder='{folder}'")
        content = cursor.fetchall()
    output = []
    if type.lower() == "docs":
        for item in content:
            output.append(items.Doc(value=item[1], user=item[2], folder=item[3]))

    elif type.lower() == "links":
        for item in content:
            output.append(items.Link(value=item[1], user=item[2], folder=item[3])) 
    return output

def set_folder(type, id, folder):
    with conn:
        cursor = conn.cursor()
        cursor.execute(f"update {type} set folder='{folder}' where id={id}")
        return True