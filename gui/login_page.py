import streamlit as st

def login_page():
    st.title("Добро пожаловать в бота медицинской помощи!")
        
    # Создание макета страницы
    col1, col2 = st.columns([2, 1])
        
    with col1:
        # Поля ввода логина и пароля, кнопка вход
        login = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        
    with col2:
        # Кнопки справа
        if st.button("Поддержка"):
            st.warning("Свяжитесь с поддержкой..."
                "       tg: @KALBkabiir")

    if login:
        with open(f"{login}.txt", "w", encoding="utf-8") as file:
            login = file.write(login)