from typing import List, Tuple

import bisect
import getch
import mutagen
import os
import time
import vlc

# The max number of times a station will "loop".
_STATION_LOOP_FACTOR = 3


def _get_time():
    return int(time.time() * 1e3)

class TrackSeeker:

    def __init__(self, track_durations_ms: List[int], get_time_fn=_get_time):
        self._track_index = []
        total_duration_ms = 0
        for duration_ms in track_durations_ms:
            total_duration_ms += duration_ms
            self._track_index.append(total_duration_ms)

        self._get_time_fn = get_time_fn

    def seek(self) -> Tuple[int, int]:
        """Seeks into list of tracks based on the current time.

        Returns:
          A tuple containing:
            1. The track index.
            2. The time position within the track in ms.
        """
        station_duration = self._track_index[-1]
        start_time_ms = self._get_time_fn() % station_duration
        track_index = bisect.bisect(self._track_index, start_time_ms)
        track_start_time_ms = start_time_ms
        if track_index:
            track_start_time_ms -= self._track_index[track_index - 1]
            
        return track_index, track_start_time_ms

class Station:

    def __init__(self, content_directory: str, vlc_instance: vlc.Instance, media_list_player: vlc.MediaListPlayer):
        self.name = os.path.basename(content_directory)
        self._populate_track_seeker_and_media_list(content_directory, vlc_instance)
        self._media_list_player = media_list_player

    def _populate_track_seeker_and_media_list(self, content_directory: str, vlc_instance: vlc.Instance) -> None:

        filepaths = []
        for path, _, files in os.walk(content_directory):
            for name in files:
                filepaths.append(os.path.join(path, name))

        # The order of play is defined by sorting the files by
        # name. For best results, do not mix subdirectories and files
        # in the same parent directory.
        filepaths.sort()

        # The track durations provided to TrackSeeker must follow the
        # same order as self._media_list. The self._media_list
        # additionally repeats files _STATION_LOOP_FACTOR times as a
        # simple way of implementing looping the playlist a ~fixed
        # number of times.
        track_durations_ms = []
        for filepath in filepaths:
            track_durations_ms.append(int(mutagen.File(filepath).info.length * 1e3))
        self._track_seeker = TrackSeeker(track_durations_ms)

        self._media_list = vlc_instance.media_list_new()
        for _ in range(_STATION_LOOP_FACTOR):
            for filepath in filepaths:
                self._media_list.add_media(vlc_instance.media_new(filepath))

    def play(self) -> None:
        self._media_list_player.set_media_list(self._media_list)

        track_index, track_start_time_ms = self._track_seeker.seek()
        self._media_list_player.play_item_at_index(track_index)
        self._media_list_player.get_media_player().set_time(track_start_time_ms)

    def is_playing(self) -> bool:
        return self._media_list_player.is_playing()

    def stop(self) -> None:
        self._media_list_player.stop()
        
class Radio:

    def __init__(self, stations_directory: str, play_keys: List[str], change_station_next_keys: List[str], change_station_previous_keys: List[str]):
        vlc_instance = vlc.Instance()
        self._media_list_player = vlc.MediaListPlayer()
        
        self._current_station_index = 0
        self._stations = self._construct_stations(stations_directory=stations_directory, vlc_instance=vlc_instance)

        self._play_keys = play_keys
        self._change_station_next_keys = change_station_next_keys
        self._change_station_previous_keys = change_station_previous_keys

    def _construct_stations(self, stations_directory: str, vlc_instance: vlc.Instance) -> List[Station]:
        stations = []
        for station_name in sorted(os.listdir(stations_directory)):
            station_path = os.path.join(stations_directory, station_name)
            stations.append(Station(content_directory=station_path, vlc_instance=vlc_instance, media_list_player=self._media_list_player))
        return stations

    def _current_station(self) -> Station:
        return self._stations[self._current_station_index]
        
    def _change_station_next(self) -> None:
        self._current_station_index = (self._current_station_index + 1) % len(self._stations)
        
    def _change_station_previous(self) -> None:
        self._current_station_index = (self._current_station_index - 1) % len(self._stations)

    def start(self) -> None:
        while True:
            command = getch.getch()
            
            if command in self._play_keys:
                if self._current_station().is_playing():
                    self._current_station().stop()
                else:
                    self._current_station().play()
            elif command in self._change_station_previous_keys:
                is_playing = self._current_station().is_playing()
                self._current_station().stop()
                self._change_station_previous()
                if is_playing:
                    self._current_station().play()   
            elif command in self._change_station_next_keys:
                is_playing = self._current_station().is_playing()
                self._current_station().stop()
                self._change_station_next()
                if is_playing:
                    self._current_station().play()   
