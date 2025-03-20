import streamlit as st

st.title("Добро пожаловать в бота медицинской помощи!")
    
# Создание макета страницы
col1, col2 = st.columns([2, 1])
    
with col1:
    # Поля ввода логина и пароля, кнопка вход
    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")

    if st.button("Вход"):
        st.success("Попытка входа...")
    
with col2:
    # Кнопки справа
    if st.button("Регистрация"):
        st.info("Переход к регистрации...")
    if st.button("Поддержка"):
        st.warning("Свяжитесь с поддержкой..."
            "       tg: @KALBkabiir")