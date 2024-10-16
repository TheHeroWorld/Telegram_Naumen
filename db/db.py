import sqlite3
import req.req as req


def new_sql():
    try:
        with sqlite3.connect("db/database.db") as db:
            cursor = db.cursor()
            query = """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                login VARCHAR,
                number INTEGER,
                clientEmployee VARCHAR,
                clientOU VARCHAR,
                auth INTEGER CHECK (auth IN (0, 1)),
                key INTEGER CHECK (auth IN (0, 1)),
                chat INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS task(
                id INTEGER PRIMARY KEY,
                task VARCHAR,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS message(
                id INTEGER PRIMARY KEY,
                message VARCHAR,
                send VARCHAR
                );
            """
            cursor.executescript(query)
    except sqlite3.Error as e:
        print(f"Error: {e}")

    
    
async def write_user_info(login, chat):
    useruid = await req.userUUID(login)
    key = await req.key(login)
    auth = "0"
    clientOU = await req.ou_request(useruid)
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        number = await req.find_contact(login)
        if number == False:
            return False
        else:
            cursor.execute("SELECT login FROM users WHERE login = ?", [login])
            if cursor.fetchone() is None:
                values = [login , chat, number, useruid, clientOU, auth, key]
                cursor.execute("INSERT INTO users(login, chat, number, clientEmployee, clientOU, auth,key) VALUES(?,?,?,?,?,?,?)", values)
                db.commit()
                db.close()
    except sqlite3.Error as e:
        print(f"Error:{e}")
        

        
async def write_unauth(login, chat, user_contact):
    useruid = "0"
    clientOU = "0"
    auth = "1"
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT login FROM users WHERE login = ?", [login])
        if cursor.fetchone() is None:
            values = [login , chat, user_contact, useruid, clientOU, auth]
            cursor.execute("INSERT INTO users(login, chat, number, clientEmployee, clientOU, auth) VALUES(?,?,?,?,?,?)", values)
            db.commit()
            db.close()
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
        
async def take_telegram():
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT login, chat FROM users",)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
        
async def find_telegram(login,chat):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT login FROM users WHERE login = ?", [login])
        if cursor.fetchone() is None:
            find = await req.userUUID(login)
            if find:
                await write_user_info(login, chat)
                return True
            else:
                return False
        else:
            return True
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
        
async def find_new_user(login):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT login FROM users WHERE login = ?", [login])
        if cursor.fetchone() is None:
            return True
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
async def take_userUUID(login):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT clientEmployee FROM users WHERE login = ?", [login])
        result = cursor.fetchone()
        employee_uuid = result[0]
        return employee_uuid
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
        
async def take_OUUID(user_uuid):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT clientOU FROM users WHERE clientEmployee = ?", [user_uuid])
        result = cursor.fetchone()
        ou = result[0]
        return ou
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
async def find_number(login):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT number FROM users WHERE login = ?", [login])
        number = cursor.fetchone()
        return number
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
        
        
async def auth(login):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT auth FROM users WHERE login = ?", [login])
        result = cursor.fetchone()
        auth = result[0]
        return auth
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
async def key(login):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT key FROM users WHERE login = ?", [login])
        result = cursor.fetchone()
        auth = result[0]
        return auth
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
async def write_task(task, login):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT id FROM users WHERE login = ?", [login])
        user_id = cursor.fetchone()
        if user_id:
            values = [str(task), user_id[0]]
            cursor.execute("INSERT INTO task(task, user_id) VALUES(?, ?)", values)
            db.commit()
            db.close()
    except sqlite3.Error as e:
        print(f"Error: {e}")
        
        
def find_task(task_id):
    try:
        with sqlite3.connect("db/database.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT users.chat
                FROM task
                INNER JOIN users ON task.user_id = users.id
                WHERE task.task = ?
            """, (task_id,))
            chat_info = cursor.fetchone()
            if chat_info:
                chat = chat_info[0]
                return chat
    except sqlite3.Error as e:
        print(f"Error: {e}")
        
        
async def find_tasks_by_login(login):
    try:
        with sqlite3.connect("db/database.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT task.task
                FROM task
                INNER JOIN users ON task.user_id = users.id
                WHERE users.login = ?
            """, (login,))
            tasks = cursor.fetchall()
            return tasks
    except sqlite3.Error as e:
        print(f"Error: {e}")
        

async def write_message(message):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        values = [str(message)]
        cursor.execute("INSERT INTO message(message, send) VALUES(?, 1)", values)
        db.commit()
        db.close()
    except sqlite3.Error as e:
        print(f"Error: {e}")

        

async def take_message(message):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute("SELECT send FROM message WHERE message = ?",[message])
        result = cursor.fetchone()
        if result:
            result = result[0]
            return result
        return "0"
    except sqlite3.Error as e:
        print(f"Error:{e}")
        
        
async def clear_table():
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM message")
        db.commit()
        db.close()
    except sqlite3.Error as e:
        print(f"Error: {e}")
        
        
async def refresh(login, chat, number):
    useruid = await req.userUUID(login)
    if useruid == None:
        useruid =await req.find_user(number)
    key = await req.key(login)
    clientOU = await req.ou_request(useruid)
    if clientOU:
        auth = "0"
    else:
        auth= "1"
    update = await update_user_info(login=login, new_chat=chat,new_number=number, new_clientEmployee=useruid, new_clientOU=clientOU,new_auth=auth, new_key=key)

async def update_user_info(login, new_chat=None, new_number=None, new_clientEmployee=None, new_clientOU=None, new_auth=None, new_key=None):
    try:
        db = sqlite3.connect("db/database.db")
        cursor = db.cursor()

        # Проверяем, существует ли пользователь с таким логином
        cursor.execute("SELECT * FROM users WHERE login = ?", [login])
        user = cursor.fetchone()
        if user is None:
            return False

        # Подготавливаем SQL-запрос для обновления данных
        update_query = "UPDATE users SET"
        update_values = []

        if new_chat is not None:
            update_query += " chat = ?,"
            update_values.append(new_chat)

        if new_number is not None:
            update_query += " number = ?,"
            update_values.append(new_number)

        if new_clientEmployee is not None:
            await req.refresh_info(login,number = new_number, uuid =new_clientEmployee)
            update_query += " clientEmployee = ?,"
            update_values.append(new_clientEmployee)
        else:
            update_query += " clientEmployee = ?,"
            update_values.append("0")

        if new_clientOU is not None:
            update_query += " clientOU = ?,"
            update_values.append(new_clientOU)
        else:
            update_query += " clientOU = ?,"
            update_values.append("0")

        if new_auth is not None:
            update_query += " auth = ?,"
            update_values.append(new_auth)
        else:
            update_query += " auth = ?,"
            update_values.append("1")

        if new_key is not None:
            update_query += " key = ?,"
            update_values.append(new_key)
        else:
            update_query += "key = ?,"
            update_values.append("1")

        # Удаляем последнюю запятую и добавляем условие WHERE
        update_query = update_query.rstrip(",") + " WHERE login = ?"
        update_values.append(login)

        # Выполняем обновление данных
        cursor.execute(update_query, update_values)
        db.commit()
        db.close()
        return True

    except sqlite3.Error as e:
        print(f"Ошибка: {e}")
        return False
