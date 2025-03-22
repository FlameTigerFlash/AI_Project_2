import streamlit as st
from login_page import login_page
from main_page import main_page
from reg_page import *
import time
import os

GigaChatKey = 'OThhMGI0MDctYzA5ZS00N2Y3LWIxYTYtOTM4NmZkZGU5YmY4Ojk5NjgwYzNiLTY4NjUtNDdhMi1hYzY2LTBlYTZmYzlkMWVkMg=='

def find_txt_file(folder_path):
    # Перебираем все файлы в папке
    for filename in os.listdir(folder_path):
        # Проверяем, что файл имеет расширение .txt
        if filename.endswith(".txt"):
            # Возвращаем имя файла без расширения
            return os.path.splitext(filename)[0]

def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login()
    elif st.session_state.page == "main":
        main_view()
    elif st.session_state.page == "register":
        registration()

def login():
    login_page()
    
    if st.button("Вход", key="login_button"):
        st.success = 'Попытка входа...'

        login = find_txt_file(os.getcwd())

        time.sleep(0.8)
        if os.path.exists(os.path.join('users', login)):
            st.info("Вы успешно авторизовались!")
            time.sleep(1)
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("Введите корректные данные!")

    if st.button("Регистрация", key="register_button"):
        st.session_state.page = "register"
        st.rerun()

def registration():
    registration_page()
    
    if st.button("Зарегистрироваться", key="register_submit"):
        time.sleep(0.8)
        st.session_state.page = "login"
        st.rerun()

def main_view():
    main_page()
    
    if st.button("Сменить пользователя", key='change'):
        st.session_state.page = "login"
        st.rerun()
        st.cache_data.clear()

if __name__ == "__main__":
    main()