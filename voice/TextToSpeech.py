import torch
import soundfile as sf


def TTS(text: str, language:str = 'ru', put_acccent:bool = False, filename='output.wav'):
    # Загрузка модели
    model, _ = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language=language,
        speaker='v4_ru'
    )

    # Параметры для улучшения естественности
    audio = model.apply_tts(
        text=text,
        speaker='baya',  # baya, aidar, kseniya, xenia, eugene, random(never)
        sample_rate=48000,
        put_accent=put_acccent,    
        put_yo=True,        
    )

    sf.write(filename, audio.numpy(), 48000)


if __name__ == "__main__":    
    TTS()
