import io

from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def split_audio_by_silence(audio_bytes, silence_thresh=-40, min_silence_len=600, bytes_format="mp3"):
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=bytes_format)
    except Exception as e:
        return None, None

    nonsilent_parts = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    if not nonsilent_parts:
        return audio_bytes, b""

    if len(nonsilent_parts) == 1:
        last_chunk = audio
        last_chunk_bytes = io.BytesIO()
        last_chunk.export(last_chunk_bytes, format=bytes_format)
        return None, last_chunk_bytes.getvalue()

    last_start, last_end = nonsilent_parts[-1]

    main_audio = audio[:last_start]
    last_chunk = audio[last_start:]

    main_audio_bytes = io.BytesIO()
    main_audio.export(main_audio_bytes, format=bytes_format)

    last_chunk_bytes = io.BytesIO()

    if last_chunk:
        last_chunk.export(last_chunk_bytes, format=bytes_format)

    return main_audio_bytes.getvalue(), last_chunk_bytes.getvalue() if last_chunk else b""
