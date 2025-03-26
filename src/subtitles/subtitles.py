import datetime
from datetime import timedelta

from srt import Subtitle

import srt


def get_subtitles_from_segments(segments, start_time: datetime.datetime) -> tuple[list[Subtitle], int]:
    subtitles = []

    start_total_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second + start_time.microsecond / 1_000_000

    for segment in segments:
        start = start_total_seconds + segment['start']
        end = start_total_seconds + segment['end']


        subtitles.append(
            Subtitle(
                index=None,
                start=timedelta(seconds=start),
                end=timedelta(seconds=end),
                content=segment['text'].strip()
            )
        )

    quantity_symbols = get_quantity_symbols(subtitles)
    # TODO check if it's correct
    print(f'quantity_symbols: {quantity_symbols}')

    return subtitles, quantity_symbols

def get_quantity_symbols(subtitles):
    return len(get_string_from_subtitles(subtitles))


def get_string_from_subtitles(subtitles: list[Subtitle]):
    return srt.compose(subtitles)
