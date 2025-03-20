import streamlit as st  # Импортируем библиотеку Streamlit для создания веб-приложений.
import pandas as pd  # Импортируем библиотеку pandas для работы с данными.
import os  # Импортируем библиотеку для работы с операционной системой, например, для работы с файлами.
import uuid  # Импортируем библиотеку для генерации уникальных идентификаторов.

def main_page():
    # Проверяем, если в сессии нет chat_id, создаем новый уникальный идентификатор.
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = str(uuid.uuid4())  # Генерация нового уникального идентификатора для чата.

    # Если в сессии нет message_id, начинаем с 1.
    if "message_id" not in st.session_state:
        st.session_state.message_id = 1  

    # Если в сессии нет переменной меню, устанавливаем значение по умолчанию как False.
    if "menu_open" not in st.session_state:
        st.session_state.menu_open = False  
    
    # Если в сессии нет сообщений, создаем пустой список сообщений.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Функция для сохранения сообщений в CSV-файл.
    def save_to_csv(chat_id, message_id, role, content):
        chat_file = f"{chat_id}.csv"  # Имя файла - это chat_id с расширением .csv.
        new_entry = pd.DataFrame([{"MessageID": message_id, "Role": role, "Content": content}])  # Формируем новый элемент данных.
        if os.path.exists(chat_file):  # Если файл уже существует, добавляем данные в конец.
            new_entry.to_csv(chat_file, mode='a', header=False, index=False, encoding="utf-8")
        else:  # Если файл не существует, создаем его с заголовками.
            new_entry.to_csv(chat_file, mode='w', header=True, index=False, encoding="utf-8")

    # Функция для загрузки истории чата из CSV-файла.
    def load_chat_history(chat_id):
        chat_file = f"{chat_id}.csv"  # Имя файла - это chat_id с расширением .csv.
        if os.path.exists(chat_file):  # Если файл существует, загружаем его.
            return pd.read_csv(chat_file, encoding="utf-8")
        return None  # Если файла нет, возвращаем None.

    # Создаем боковую панель (sidebar) с кнопками для взаимодействия с чатом.
    with st.sidebar:
        # Кнопка для открытия или закрытия меню истории чатов.
        if st.button("История чатов"):
            st.session_state.menu_open = not st.session_state.menu_open
        
        if st.session_state.menu_open:
            # Получаем список файлов чатов (CSV) в текущей директории.
            chat_files = [f.split(".")[0] for f in os.listdir() if f.endswith(".csv")]
            chat_names = []  # Список для хранения имен чатов.

            # Загружаем первый запрос чата из каждого файла.
            for chat_id in chat_files:
                df = load_chat_history(chat_id)
                if df is not None and not df.empty:
                    first_message = df.iloc[0]["Content"]
                    chat_names.append((chat_id, first_message))

            # Создаем выпадающий список для выбора чата.
            selected_chat_name = st.selectbox("Выберите чат", [chat[1] for chat in chat_names], index=None, placeholder="Выберите чат")
            
            if selected_chat_name:
                # Находим chat_id, соответствующий выбранному чату.
                selected_chat_id = next(chat[0] for chat in chat_names if chat[1] == selected_chat_name)
                if st.button("Открыть чат"):
                    # Если нажали кнопку "Открыть чат", загружаем историю и отображаем сообщения.
                    st.session_state.chat_id = selected_chat_id
                    st.session_state.messages = []
                    history = load_chat_history(selected_chat_id)
                    if history is not None:
                        st.session_state.messages = [{"role": row["Role"], "content": row["Content"]} for _, row in history.iterrows()]

        # Кнопка для начала нового чата.
        if st.button("Начать новый чат"):
            # Генерация нового уникального chat_id и сброс состояния.
            st.session_state.chat_id = str(uuid.uuid4())
            st.session_state.message_id = 1
            st.session_state.messages = []
            st.session_state.menu_open = False

    # Создаем две колонки: одна для чата, другая для изображений и дополнительной информации.
    col1, col2 = st.columns([3, 1])

    # В первой колонке выводим сообщения чата.
    with col1:
        chat_container = st.container()  # Контейнер для сообщений чата.
        with chat_container:
            # Отображаем все сообщения чата.
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # Поле для ввода сообщения.
        with st.container():
            col1_input, col2_input = st.columns([9, 1])
            with col1_input:
                prompt = st.chat_input("Расскажите о своей проблеме...")

        if prompt:
            message_id = st.session_state.message_id  # Берем текущий message_id.
            if st.session_state.chat_id:
                history = load_chat_history(st.session_state.chat_id)
                if history is not None and not history.empty:
                    message_id = int(history["MessageID"].max()) + 1  # Получаем максимальный ID сообщения и увеличиваем на 1.
            
            # Добавляем сообщение пользователя.
            user_message = {"role": "user", "content": prompt}
            st.session_state.messages.append(user_message)
            save_to_csv(st.session_state.chat_id, message_id, "user", prompt)
            
            # Отображаем сообщение пользователя.
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            # Генерация ответа от бота.
            response = f"Ответ на: {prompt}"
            message_id += 1
            assistant_message = {"role": "assistant", "content": response}
            st.session_state.messages.append(assistant_message)
            save_to_csv(st.session_state.chat_id, message_id, "assistant", response)
            
            # Отображаем ответ бота.
            with chat_container:
                with st.chat_message("assistant"):
                    st.markdown(response)
            
            # Обновляем message_id для следующего сообщения.
            st.session_state.message_id = message_id + 1

    # Во второй колонке отображаем изображение и заголовок.
    with col2:
        image_path = "red-cross.jpeg"
        st.image(image_path, caption="Напоминалки от бота сюда.")  # Показываем изображение.
        st.title("Либо сюда.")  # Заголовок.
