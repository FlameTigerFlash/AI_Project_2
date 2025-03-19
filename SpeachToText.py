import sounddevice as sd
import numpy as np
import whisper
from scipy.io.wavfile import write
import torch
import os



model = whisper.load_model("base")


# Функция для записи аудио
def record_audio(duration = 5, sample_rate=16000):
    print("Запись началась...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Ждем окончания записи
    print("Запись завершена.")
    return audio.flatten()


# Функция для сохранения аудио в формате WAV
def save_audio(audio, sample_rate=16000, filename="output.wav"):
    write(filename, sample_rate, (audio * 32767).astype(np.int16))


# Функция для синтеза речи
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()



def main():
    # Запись аудио
    duration = 5  # Длительность записи в секундах (PLACEHOLDER)
    audio = record_audio(duration)
    save_audio(audio)

    # Преобразование аудио в текст
    result = model.transcribe("output.wav")
    text = result["text"]
    print(f"Распознанный текст: {text}")

    os.remove("output.wav")
    return text  


if __name__ == "__main__":
    main()
