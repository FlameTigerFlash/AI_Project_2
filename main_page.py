import streamlit as st
import pandas as pd
import os
import uuid

# Инициализация переменных в session_state, если их нет
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

if "message_id" not in st.session_state:
    st.session_state.message_id = 1  

if "menu_open" not in st.session_state:
    st.session_state.menu_open = False  

# Функция для сохранения сообщений в CSV
# Каждый чат сохраняется в отдельный файл chat_id.csv
def save_to_csv(chat_id, message_id, role, content):
    chat_file = f"{chat_id}.csv"
    new_entry = pd.DataFrame([{"MessageID": message_id, "Role": role, "Content": content}])
    if os.path.exists(chat_file):
        new_entry.to_csv(chat_file, mode='a', header=False, index=False, encoding="utf-8")
    else:
        new_entry.to_csv(chat_file, mode='w', header=True, index=False, encoding="utf-8")

# Функция для загрузки истории чата из CSV
def load_chat_history(chat_id):
    chat_file = f"{chat_id}.csv"
    if os.path.exists(chat_file):
        return pd.read_csv(chat_file, encoding="utf-8")
    return None

# Инициализация списка сообщений, если его нет в session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Боковая панель (sidebar)
with st.sidebar:
    if st.button("История чатов"):
        st.session_state.menu_open = not st.session_state.menu_open
    
    # Если меню открыто, показываем список доступных чатов
    if st.session_state.menu_open:
        chat_files = [f.split(".")[0] for f in os.listdir() if f.endswith(".csv")]
        chat_names = []

        for chat_id in chat_files:
            df = load_chat_history(chat_id)
            if df is not None and not df.empty:
                first_message = df.iloc[0]["Content"]  # Берем первый текст в чате
                chat_names.append((chat_id, first_message))

        selected_chat_name = st.selectbox("Выберите чат", [chat[1] for chat in chat_names], index=None, placeholder="Выберите чат")
        
        # Если выбран чат, находим его ID и загружаем историю
        if selected_chat_name:
            selected_chat_id = next(chat[0] for chat in chat_names if chat[1] == selected_chat_name)
            
            if st.button("Открыть чат"):
                st.session_state.chat_id = selected_chat_id
                st.session_state.messages = []
                history = load_chat_history(selected_chat_id)
                if history is not None:
                    for _, row in history.iterrows():
                        st.session_state.messages.append({"role": row["Role"], "content": row["Content"]})

    # Кнопка для начала нового чата
    if st.button("Начать новый чат"):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.message_id = 1
        st.session_state.messages = []
        st.session_state.menu_open = False
    
    # Кнопка для смены пользователя
    if st.button("Сменить пользователя"):
        st.experimental_rerun()  # Заглушка: можно заменить на код для перехода на другую страницу

# Основной интерфейс
col1, col2 = st.columns([3, 1])

with col1:
    chat_container = st.container()

    # Отображение сообщений из истории чатов
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Поле ввода сообщения
    with st.container():
        col1_input, col2_input = st.columns([9, 1])
        with col1_input:
            prompt = st.chat_input("Расскажите о своей проблеме...")

    if prompt:
        message_id = st.session_state.message_id
        history = load_chat_history(st.session_state.chat_id)
        if history is not None and not history.empty:
            st.session_state.messages = [{"role": row["Role"], "content": row["Content"]} for _, row in history.iterrows()]
            message_id = int(history["MessageID"].max()) + 1

        # Сохранение пользовательского сообщения
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_to_csv(st.session_state.chat_id, message_id, "user", prompt)

        # Отображение пользовательского сообщения
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Ответ ассистента
        response = f"Ответ на: {prompt}"
        message_id += 1
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_to_csv(st.session_state.chat_id, message_id, "assistant", response)

        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(response)

        st.session_state.message_id = message_id + 1

    # Автопрокрутка вниз
    st.components.v1.html("""
        <script>
            window.scrollTo(0, document.documentElement.scrollHeight);
        </script>
    """, height=0)

# Второй столбец (колонка справа)
with col2:
    image_path = "red-cross.jpeg"
    st.image(image_path, caption="Напоминалки от бота сюда.")

    st.title("Либо сюда.")