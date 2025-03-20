import torch
import soundfile as sf


def TTS():
    # Загрузка модели
    model, _ = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language='ru',
        speaker='v4_ru'
    )

    # Параметры для улучшения естественности
    audio = model.apply_tts(
        text="Условие: Среди 6 ключей три подходят к двери. Ключи пробуют один за одним, пока не откроют дверь. Найти закон распределения числа опробованных ключей. Вычислить математическое ожидание и дисперсию числа опробованных ключей.",
        speaker='baya',  # baya, aidar, kseniya, xenia, eugene, random(never)
        sample_rate=48000,
        put_accent=True,    
        put_yo=True,        
    )

    sf.write('output.wav', audio.numpy(), 48000)


if __name__ == "__main__":    
    TTS()
