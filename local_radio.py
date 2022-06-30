from typing import List, Tuple

import bisect
import getch
import mutagen
import os
import time
import vlc

# The max number of times a station will "loop".
_STATION_LOOP_FACTOR = 3

# If (len(stations) * 2) inputs are received within this period,
# additional inputs are ignored.
_INPUT_TIMEOUT_WINDOW_MS = 30 * 1e3


def _get_start_time_ms(station_duration: int) -> int:
    return int(time.time() * 1e3) % station_duration

class Station:

    def __init__(self, content_directory: str, vlc_instance: vlc.Instance, media_list_player: vlc.MediaListPlayer):
        self.name = os.path.basename(content_directory)
        self._populate_track_index_and_media_list(content_directory, vlc_instance)
        self._media_list_player = media_list_player

    def _populate_track_index_and_media_list(self, content_directory: str, vlc_instance: vlc.Instance) -> None:

        filepaths = []
        for path, _, files in os.walk(content_directory):
            for name in files:
                filepaths.append(os.path.join(path, name))

        # The order of play is defined by sorting the files by
        # name. For best results, do not mix subdirectories and files
        # in the same parent directory.
        filepaths.sort()

        # The self._track_index must follow the same order as
        # self._media_list. The self._media_list additionally repeats
        # files _STATION_LOOP_FACTOR times as a simple way of
        # implementing looping the playlist a ~fixed number of times.
        self._track_index = []
        total_duration_ms = 0
        for filepath in filepaths:
            file_duration_ms = int(mutagen.File(filepath).info.length * 1e3)
            total_duration_ms += file_duration_ms
            self._track_index.append(total_duration_ms)

        self._media_list = vlc_instance.media_list_new()
        for _ in range(_STATION_LOOP_FACTOR):
            for filepath in filepaths:
                self._media_list.add_media(vlc_instance.media_new(filepath))

    def _duration(self) -> int:
        return self._track_index[-1]

    def _get_track_index(self, start_time_ms: int) -> int:
        return bisect.bisect_left(self._track_index, start_time_ms)

    def _get_track_start_time_ms(self, start_time_ms: int, track: int) -> int:
        if track:
            return start_time_ms - self._track_index[track - 1]
            
        return start_time_ms
    
    def play(self) -> None:
        self._media_list_player.set_media_list(self._media_list)

        start_time_ms = _get_start_time_ms(self._duration())
        track = self._get_track_index(start_time_ms)
        track_start_time_ms = self._get_track_start_time_ms(start_time_ms, track)

        self._media_list_player.play_item_at_index(track)
        self._media_list_player.get_media_player().set_time(track_start_time_ms)

class Radio:

    def __init__(self, stations_directory: str, play_keys: List[str], next_station_keys: List[str], previous_station_keys: List[str]):
        vlc_instance = vlc.Instance()
        self._media_list_player = vlc.MediaListPlayer()
        
        self._current_station_index = 0
        self._stations = self._construct_stations(stations_directory=stations_directory, vlc_instance=vlc_instance)
        self._input_timeout_circular_buffer = [0] * (len(self._stations) * 2)
        self._input_timeout_index = 0

    def _construct_stations(self, stations_directory: str, vlc_instance: vlc.Instance) -> List[Station]:
        stations = []
        for station_name in sorted(os.listdir(stations_directory)):
            station_path = os.path.join(stations_directory, station_name)
            stations.append(Station(content_directory=station_path, vlc_instance=vlc_instance, media_list_player=self._media_list_player))
        return stations

    def _pause(self) -> None:
        self._media_list_player.pause()

    def _play(self) -> None:
        self._stations[self._current_station_index].play()

    def _next_station(self) -> None:
        self._current_station_index = (self._current_station_index + 1) % len(self._stations)
        
    def _previous_station(self) -> None:
        self._current_station_index = (self._current_station_index - 1) % len(self._stations)

    def _should_ignore_input(self) -> bool:
        self._input_timeout_circular_buffer[self._input_timeout_index] = int(time.time() * 1e3)
        newest_input_time_ms = self._input_timeout_circular_buffer[self._input_timeout_index]
        self._input_timeout_index = (self._input_timeout_index + 1) % len(self._input_timeout_circular_buffer)
        oldest_input_time_ms = self._input_timeout_circular_buffer[self._input_timeout_index]
        return (newest_input_time_ms - oldest_input_time_ms) < _INPUT_TIMEOUT_WINDOW_MS
        
    def start(self) -> None:
        while True:
            command = getch.getch()
            if self._should_ignore_input():
                continue
            
            if command in play_keys:
                if self._media_list_player.is_playing():
                    self._pause()
                else:
                    self._play()
            elif command in previous_station_keys:
                self._previous_station()
                if self._media_list_player.is_playing():
                    self._play()   
            elif command in next_station_keys:
                self._next_station()
                if self._media_list_player.is_playing():
                    self._play()   

stations_directory = "/home/lyric/Documents/local-radio/stations"
play_keys = ['a', 's', 'd']
previous_station_keys = ['q', 'w', 'e']
next_station_keys = ['z', 'x', 'c']

radio = Radio(stations_directory=stations_directory, play_keys=play_keys, previous_station_keys=previous_station_keys, next_station_keys=next_station_keys)
radio.start()
