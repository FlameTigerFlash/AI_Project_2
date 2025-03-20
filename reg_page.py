import streamlit as st

def registration_page():
    st.title("Регистрация в боте медицинской помощи")
        
    # Поля для регистрации
    first_name = st.text_input("Имя")
    last_name = st.text_input("Фамилия")
    middle_name = st.text_input("Отчество")
    age = st.number_input("Возраст", min_value=0, max_value=120, step=1)
    medical_info = st.text_area("Медицинские особенности")
        
    # Поля логина и пароля
    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")
