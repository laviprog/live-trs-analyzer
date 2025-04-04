import asyncio
import copy
import io
import json
import subprocess
import threading

from datetime import datetime, timedelta
from collections import deque

from pydub import AudioSegment
from srt import Subtitle

from src.bot.sender import send
from src.model.requests import chat_completions
from src.process_flow import logger
from src.process_flow.detection import split_audio_by_silence
from src.subtitles.subtitles import get_subtitles_from_segments, get_quantity_symbols, get_string_from_subtitles
from src.transcriber.transcribe import transcribe_audio


class Listener(threading.Thread):
    def __init__(self, flow, keywords, language, analyzer_model, loop, sample_rate=16000, flow_format="mp3"):
        super().__init__()
        self.flow = flow
        self.keywords = keywords
        self.sample_rate = sample_rate
        self.flow_format = flow_format
        self.language = language
        self.analyzer_model = analyzer_model
        self.loop = loop

        self.buffer = io.BytesIO()
        self.remaining = b""

        self.subtitles: deque[list[Subtitle]] = deque()
        self.total_subtitles_symbols = 0
        self.total_time = timedelta(seconds=0)
        self.max_subtitles_symbols_window = 3000  # mb selectable value
        self.max_subtitles_symbols = 8000  # mb selectable value, < 000
        self.max_time_before = timedelta(seconds=5 * 60)  # 5 min
        self.max_time = timedelta(seconds=15 * 60)  # 15 min

        self.word_tracking = {}
        # {
        #   word: {
        #           subtitles (copy): [],
        #           total_subtitles_symbols: 0,
        #           total_time: 0,
        #         }
        # }

        self.time = datetime.now()

        self._stop_event = threading.Event()

    def run(self):
        logger.info("Start listen process")

        process = subprocess.Popen(
            ["ffmpeg", "-i", self.flow, "-ac", "1", "-ar", str(self.sample_rate), "-f", self.flow_format, "pipe:1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10 ** 9
        )

        try:
            while not self._stop_event.is_set():
                chunk = process.stdout.read(81920)

                if not chunk or self._stop_event.is_set():
                    break

                self.buffer.write(chunk)
                self.buffer.seek(0)
                audio_bytes = self.buffer.read()
                self.buffer.seek(0)
                self.buffer.truncate(0)

                total_audio_bytes = self.remaining + audio_bytes

                logger.info(f"total_audio_bytes: {len(total_audio_bytes)}")
                logger.info(f"starting split audio by silence")

                main_audio, last_chunk = split_audio_by_silence(
                    audio_bytes=total_audio_bytes,
                    bytes_format=self.flow_format
                )

                if self._stop_event.is_set():
                    break

                self.remaining = last_chunk or b""

                if main_audio:
                    main_audio_segment = AudioSegment.from_file(io.BytesIO(main_audio), format=self.flow_format)
                    main_duration = len(main_audio_segment) / 1000.0

                    logger.info(f"Processing audio segment (duration: {main_duration} seconds)")

                    self.time += timedelta(seconds=main_duration)

                    logger.info(f"Now time: {self.time}")

                    if self._stop_event.is_set():
                        break

                    logger.info(f"Send to transcribe")

                    segments = transcribe_audio(main_audio, language=self.language)
                    if not segments:
                        continue
                    subtitles, quantity_symbols = get_subtitles_from_segments(segments, self.time)

                    self.total_subtitles_symbols += quantity_symbols
                    self.total_time += timedelta(seconds=main_duration)
                    self.subtitles.append(subtitles)

                    while (self.total_subtitles_symbols >= self.max_subtitles_symbols_window or
                           self.total_time >= self.max_time_before):
                        subtitles = self.subtitles.popleft()
                        self.total_subtitles_symbols -= get_quantity_symbols(subtitles)
                        self.total_time -= subtitles[-1].end - subtitles[0].start

                    words = self._check_key_words(subtitles)

                    logger.info(f"word_tracking: {self.word_tracking}")

                    words_ready = []
                    for word in words:
                        if word not in self.word_tracking:
                            words_ready.append(word)
                            logger.info(f"Adding word '{word}' to word_tracking")
                            logger.info(f"queue: {self.subtitles}, len(subtitles): {len(subtitles)}")
                            self.word_tracking[word] = {
                                "subtitles": list(copy.deepcopy(self.subtitles)),
                                "total_subtitles_symbols": self.total_subtitles_symbols,
                                "total_time": self.subtitles[-1][-1].end - self.subtitles[0][0].start,
                            }

                    words = list(self.word_tracking.keys())

                    for word in words:
                        if word in words_ready:
                            continue

                        logger.info(f"Next word {word}")

                        self.word_tracking[word]["subtitles"].append(subtitles)
                        self.word_tracking[word]["total_subtitles_symbols"] += quantity_symbols
                        self.word_tracking[word]["total_time"] += subtitles[-1].end - subtitles[0].start

                        logger.info(f"word_tracking: {self.word_tracking[word]}")
                        if (self.word_tracking[word]["total_time"] >= self.max_time
                                or self.word_tracking[word]["total_subtitles_symbols"] >= self.max_subtitles_symbols):
                            subtitles_list = self.word_tracking.pop(word)["subtitles"]

                            subtitles = [subtitles_list[i][j] for i in range(len(subtitles_list)) for j in range(len(subtitles_list[i]))]

                            str_subtitles = get_string_from_subtitles(subtitles)

                            logger.info(f"srt_subtitles: {str_subtitles}")

                            prompt = (
                                f"Keyword: {word}."
                                f"Subtitles:\n{str_subtitles}"
                            )

                            logger.info(f"Send to model request: {prompt}")

                            if self._stop_event.is_set():
                                break

                            start_time_model_processing = datetime.now()
                            result = asyncio.run_coroutine_threadsafe(chat_completions(self.analyzer_model, prompt), self.loop).result(timeout=20)
                            end_time_model_processing = datetime.now()

                            if self._stop_event.is_set():
                                break

                            logger.info(f"Processing time model (seconds): {(end_time_model_processing - start_time_model_processing).seconds}")
                            logger.info(f"Result: {result}")
                            try:
                                result = json.loads(result)
                            except json.decoder.JSONDecodeError:
                                result = {"result": result}
                            '''
                            {
                              "time_range": "HH:MM:SS – HH:MM:SS",
                              "tone": "tone",
                              "summary": "summary"
                            }
                            '''
                            asyncio.run_coroutine_threadsafe(send(result, word), self.loop).result(timeout=10)

                self.remaining = last_chunk or b""

                if self._stop_event.is_set():
                    break

        finally:
            if process.poll() is not None:
                logger.info("Terminating ffmpeg process...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.info("Process timed out.")

    def _check_key_words(self, subtitles: list[Subtitle]):
        words = set()

        for keyword in self.keywords:
            for subtitle in subtitles:
                if keyword in subtitle.content.lower():
                    words.add(keyword)

        return list(words)

    def stop(self):
        logger.info("Stopping listener...")
        self._stop_event.set()
