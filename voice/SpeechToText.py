import speech_recognition as sr

def STT(audio_path):
    recognizer = sr.Recognizer()
    
    # Открываем аудиофайл
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)  # Считываем файл
    
    try:
        text = recognizer.recognize_google(audio_data, language="ru-RU")  # Распознаем голос (русский)
        return text
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError:
        return "Ошибка при запросе к сервису распознавания"