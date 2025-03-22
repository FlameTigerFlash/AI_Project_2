import torch
import soundfile as sf
import numpy as np
import re

def split_text(text, max_length=150):
    """ Разбивает текст на части по предложениям (точкам и другим знакам). """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def TTS(text: str, language: str = 'ru', put_accent: bool = False, filename='output.wav'):
    # Загрузка модели
    model, _ = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language=language,
        speaker='v4_ru'
    )

    text_chunks = split_text(text)
    audio_list = []

    for chunk in text_chunks:
        audio = model.apply_tts(
            text=chunk,
            speaker='baya',  
            sample_rate=48000,
            put_accent=put_accent,    
            put_yo=True,        
        )
        audio_list.append(audio.numpy())

    # Объединяем все части в один аудиофайл
    final_audio = np.concatenate(audio_list)
    sf.write(filename, final_audio, 48000)

if __name__ == "__main__":    
    long_text = "Привет! Это тестовый текст для проверки длинного аудиофайла. " \
                "Система должна уметь разбивать его на части и корректно соединять. " \
                "Надеюсь, это сработает."
    
    TTS(long_text)
