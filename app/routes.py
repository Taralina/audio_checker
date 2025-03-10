from fastapi import APIRouter, File, UploadFile, HTTPException
import wave
import io

router = APIRouter()

# Эталонные параметры аудиофайла
REFERENCE_FORMAT = {
    "nchannels": 1,          # Моно
    "sampwidth": 2,          # 16 бит (2 байта)
    "framerate": 44100,      # Частота дискретизации
    "max_duration": 10       # Максимальная длительность в секундах
}

@router.post("/check-audio/")
async def check_audio(file: UploadFile = File(...)):
    """
    Принимает аудиофайл и проверяет его формат.
    
    - **file**: WAV файл для проверки
    - **Возвращает**: JSON с сообщением о корректности формата
    """
    if file.content_type not in ["audio/wav", "audio/x-wav"]:
        raise HTTPException(status_code=400, detail="Неверный MIME-тип файла. Ожидается WAV.")
    
    try:
        data = await file.read()
        with wave.open(io.BytesIO(data), 'rb') as wav_file:
            params = wav_file.getparams()
            duration = params.nframes / params.framerate
            
            errors = []
            if params.nchannels != REFERENCE_FORMAT["nchannels"]:
                errors.append(f"Ожидается {REFERENCE_FORMAT['nchannels']} канал(а), получено {params.nchannels}.")
            if params.sampwidth != REFERENCE_FORMAT["sampwidth"]:
                errors.append(f"Ожидается {REFERENCE_FORMAT['sampwidth'] * 8}-битный звук, получено {params.sampwidth * 8}-битный.")
            if params.framerate != REFERENCE_FORMAT["framerate"]:
                errors.append(f"Ожидается частота дискретизации {REFERENCE_FORMAT['framerate']} Гц, получено {params.framerate} Гц.")
            if duration > REFERENCE_FORMAT["max_duration"]:
                errors.append(f"Длительность файла {duration:.2f} сек превышает {REFERENCE_FORMAT['max_duration']} сек.")
            
            if errors:
                raise HTTPException(status_code=400, detail={"message": "Формат аудиофайла неверный", "errors": errors})
            
            return {"message": "Формат аудиофайла корректный"}
    
    except wave.Error:
        raise HTTPException(status_code=400, detail="Файл не является корректным WAV.")
