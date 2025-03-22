import streamlit as st
import os
import csv
import uuid

def save_user_data(user_data, user_login):
    user_id = user_login  # Генерация уникального ID пользоват   
    user_folder = os.path.join("users", user_id)
    os.makedirs(user_folder, exist_ok=True)  # Создание папки пользователя
    
    file_path = os.path.join(user_folder, "info.csv")
    
    # Запись данных в CSV
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["name", "gender", "age", "weight", "height", "allergies", "personal_file", "login", "password"])
        writer.writerow(user_data)

def registration_page():
    st.title("Регистрация в боте медицинской помощи")
    
    # Поля для регистрации
    full_name = st.text_input("ФИО")
    gender = st.selectbox("Пол", ["Мужской", "Женский"])
    age = st.number_input("Возраст", min_value=0, max_value=120, step=1)
    weight = st.number_input("Вес (кг)", min_value=0.0, max_value=300.0, step=0.1)
    height = st.number_input("Рост (см)", min_value=0.0, max_value=250.0, step=0.1)
    allergies = st.text_area("Аллергии")
    medical_info = st.text_area("О здоровье (хронические болезни, уровень физической активности и т.д.)")
    
    # Поля логина и пароля
    login = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")
    
    user_data = [full_name, gender, age, weight, height, allergies, medical_info, login, password]
    save_user_data(user_data, login)
