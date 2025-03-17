import asyncio
import io
import subprocess
from datetime import datetime

from src.process_flow.detection import split_audio_by_silence
from src.transcriber.transcribe import transcribe_audio


class Listener:
    buffer = io.BytesIO()
    remaining = b""
    subtitles = []

    time = datetime.now()

    def __init__(self, flow, key_words, language, analyzer_model, sample_rate=16000, flow_format="mp3"):
        self.flow = flow
        self.key_words = key_words
        self.sample_rate = sample_rate
        self.flow_format = flow_format
        self.language = language
        self.analyzer_model = analyzer_model

    async def listen(self):
        process = subprocess.Popen(
            ["ffmpeg", "-i", self.flow, "-ac", "1", "-ar", self.sample_rate, "-f", self.flow_format, "pipe:1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10 ** 8
        )

        try:
            while True:
                chunk = await asyncio.to_thread(process.stdout.read, 81920)

                if not chunk:
                    break

                self.buffer.write(chunk)
                self.buffer.seek(0)
                audio_bytes = self.buffer.read()
                self.buffer.seek(0)
                self.buffer.truncate(0)

                total_audio_bytes = self.remaining + audio_bytes

                main_audio, last_chunk = await split_audio_by_silence(total_audio_bytes, bytes_format=self.flow_format)

                if main_audio:
                    segments = await transcribe_audio(main_audio, language=self.language)


                    # TODO
                    # Расстановка таймингов
                    # Окно субтитров
                    # При появлении отлеживаемого слова добавляем отслеживание в очередь
                    # При завершении отслеживания отправляем запрос в модель для анализа
                    # Получаем ответ и отправляем запрос за видео с таймингами, которые вернула модель
                    # Полученное видео и субтитры отправляем клиенту
                    #
                    # subtitles = await get_subtitles_from_segments(segments, total_audio_time)

                    # today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                    #
                    #
                    # total_audio_time += main_duration

                self.remaining = last_chunk or b""

        finally:
            process.terminate()



async def start_listen(flow, key_words, model, language="en"):
    listener = Listener(flow, key_words, language, model)

    await listener.listen()

    # model send to analyze