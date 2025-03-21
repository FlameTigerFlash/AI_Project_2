import psycopg2
import re

# создание бд
def create_database():
    conn = psycopg2.connect(
        host="localhost",
        port="6379",  # чаще всего по умолчанию 5432
        database="mydatabase", #как назовете
        user="postgres",
        password="PostgreSQL" # в теории логин и пароль такие по умолчанию
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


"""
    Проверяет, что пароль:
    - Содержит хотя бы одну заглавную букву.
    - хотя бы одну цифру.
    - хотя бы один знак препинания.
    - Длина пароля не менее 6 символов.
"""

def is_password_valid(password):
    if len(password) < 6:
        return False, "Пароль должен быть не менее 6 символов."
    if not re.search(r"[A-Z]", password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву."
    if not re.search(r"\d", password):
        return False, "Пароль должен содержать хотя бы одну цифру."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Пароль должен содержать хотя бы один знак препинания."
    return True, "Пароль валиден."

# комменты выше можно выводить пользователю и перезапускать процесс
# Функция для проверки вводимых данных
"""
    Проверяет, что вводимые данные:
    - Не пустые.
    - Содержат только допустимые символы (буквы, цифры, пробелы, знаки препинания).
"""
def is_input_valid(input_data):
    if not input_data.strip():
        return False, "Введенные данные не могут быть пустыми."
    if not re.match(r"^[a-zA-Z0-9\s!@#$%^&*(),.?\":{}|<>]+$", input_data):
        return False, "Введенные данные содержат недопустимые символы."
    return True, "Введенные данные валидны."

# Функция для регистрации пользователя
def register_user(username, password):
    conn = psycopg2.connect(
        host="localhost",
        port="6379",
        database="mydatabase",
        user="postgres",
        password="PostgreSQL"
    )
    cursor = conn.cursor()
    try:
        # Проверка валидности пароля
        is_pass_valid, pass_message = is_password_valid(password)
        if not is_pass_valid:
            print(pass_message)
            return
        # Проверка валидности юзернейма
        is_username_valid, username_message = is_input_valid(username)
        if not is_username_valid:
            print(username_message)
            return
        # Проверка, существует ли юзернейм
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print("Ошибка: Юзернейм уже занят.")
            return

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        print("Пользователь успешно зарегистрирован!")

    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
    except psycopg2.IntegrityError as e:
        print(f"Ошибка при регистрации пользователя: {e}")
    finally:
        cursor.close()
        conn.close()

# добавление сообщения в логи, можно добавить слобец: от кого сообщение (юзер/бот)
def add_log(user_id, message):
    if is_input_valid(message):
        conn = psycopg2.connect(
            host="localhost",
            port="6379",
            database="mydatabase",
            user="postgres",
            password="PostgreSQL"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (user_id, message) VALUES (%s, %s)", (user_id, message))
        conn.commit()
        cursor.close()
        conn.close()
    else:
        print("Ошибка: Недопустимые символы в сообщении.")


# получение всех логов по id
def get_user_logs(user_id):
    conn = psycopg2.connect(
        host="localhost",
        port="6379",
        database="mydatabase",
        user="postgres",
        password="PostgreSQL"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM logs WHERE user_id = %s ORDER BY timestamp", (user_id,))
    return cursor.fetchall()

# удаление по юзернейм
def delete_user_by_username(username):
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="6379",
            database="mydatabase",
            user="postgres",
            password="PostgreSQL"
        )
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()

        if user_id:
            user_id = user_id[0]

            cursor.execute("DELETE FROM logs WHERE user_id = %s", (user_id,))

            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

            conn.commit()
            print(f"Пользователь {username} и все его логи успешно удалены.")
        else:
            print(f"Пользователь с username {username} не найден.")

    except psycopg2.Error as e:
        print(f"Ошибка при удалении пользователя: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

# удаление по id
def delete_user_by_id(user_id):

    try:
        conn = psycopg2.connect(
            host="localhost",
            port="6379",
            database="mydatabase",
            user="postgres",
            password="PostgreSQL"
        )
        cursor = conn.cursor()

        cursor.execute("DELETE FROM logs WHERE user_id = %s", (user_id,))

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

        conn.commit()
        print(f"Пользователь с ID {user_id} и все его логи успешно удалены.")

    except psycopg2.Error as e:
        print(f"Ошибка при удалении пользователя: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
