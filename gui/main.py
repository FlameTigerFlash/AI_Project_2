import streamlit as st
from login_page import login_page
from main_page import main_page
from reg_page import registration_page
import time

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
        time.sleep(0.8)
        st.session_state.page = "main"
        st.rerun()
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