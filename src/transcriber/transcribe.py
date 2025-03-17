import io
import torchaudio

from src.transcriber import logger, MODEL


async def transcribe_audio(audio_bytes, language="en", batch_size=4, chunk_size=10):
    try:
        audio, _ = torchaudio.load(io.BytesIO(audio_bytes))
    except Exception as e:
        logger.error(f"Error loading audio file for transcription: {e}")
        return None

    logger.info("Audio file loaded successfully. Running transcription model.")
    try:
        audio = audio.squeeze().numpy()
        result = MODEL.transcribe(audio, batch_size=batch_size, chunk_size=chunk_size, language=language)
    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return None

    logger.info(f"Transcription completed successfully. Result: {result['segments']}")
    return result["segments"]