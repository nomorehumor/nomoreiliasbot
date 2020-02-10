import psycopg2
import items

conn = psycopg2.connect(user='Max',database='postgres', host='localhost')

def save_user(chat_id):
    if not check_user_connected(chat_id):
        try:
            cursor = conn.cursor()
            cursor.execute(f'insert into connected_users (chat_id) values ({chat_id})')
            print(f"Added user with chat_id = {chat_id} to table")
        except Exception:
            print('sql error in save_user')
        finally: 
            conn.commit()
            cursor.close()

def check_user_connected(chat_id):
    is_user_in_table = False
    try:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM connected_users WHERE chat_id=({chat_id})')
        if cursor.fetchall():
            is_user_in_table = True
            print(f'user with chat id {chat_id} has connected previously')
    except Exception:
        print('sql error in check_user_connected')
    finally: 
        conn.commit()
        cursor.close()
    return is_user_in_table


def get_connected_users():
    users = []
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM connected_users')
        users = cursor.fetchall()
    except Exception:
        print('sql error in get_commected_users')
    finally: 
        conn.commit()
        cursor.close()
    return users

def save_doc(value, username):
    id = 0
    try:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO docs (value, linkeduser, folder) VALUES ('{value}', '{username}', 'COMMON') RETURNING id")
        output = cursor.fetchall()
        id = output[0][0]
    except Exception as error:
        print('sql error in save_doc', error)
    finally: 
        conn.commit()
        cursor.close()
    return id
    

    
def save_link(value, username):
    id = 0
    try:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO links (value, linkeduser, folder) VALUES ('{value}', '{username}', 'COMMON') RETURNING id")
        output = cursor.fetchall()
        id = output[0][0]
    except Exception:
        print('sql error in save_link')
    finally: 
        conn.commit()
        cursor.close()
    return id


def get_content(type, folder):
    content = []
    try:
        cursor = conn.cursor()
        cursor.execute(f"select * from {type} where folder='{folder}'")
        content = cursor.fetchall()
    except Exception:
        print('sql error in get_content')
    finally: 
        conn.commit()
        cursor.close()
    output = []
    if type.lower() == "docs":
        for item in content:
            output.append(items.Doc(value=item[0], user=item[1], folder=item[3]))

    elif type.lower() == "links":
        for item in content:
            output.append(items.Link(value=item[1], user=item[2], folder=item[3])) 
            
    return output

def set_folder(type, id, folder):
    try:
        cursor = conn.cursor()
        cursor.execute(f"update {type} set folder='{folder}' where id={id}")
        return True
    except Exception as error:
        print("sql error in set_folder", error)
    finally:
        conn.commit()
        cursor.close()
        return True
    