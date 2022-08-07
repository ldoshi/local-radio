from typing import List

import local_radio
import spotipy

# Spotify access.
_SPOTIPY_CLIENT_ID='ENTER HERE'
_SPOTIPY_CLIENT_SECRET='ENTER HERE'
_SPOTIPY_REDIRECT_URI='http://localhost'
_SPOTIFY_SCOPE = ["user-modify-playback-state", "user-read-playback-state", "user-read-currently-playing", "playlist-read-private", "playlist-read-collaborative", "app-remote-control", "streaming", "user-library-read"]

# Spotify player.
_DEVICE_ID = "ENTER HERE"


def main():

    stations_directory = "/home/lyric/Documents/local-radio/stations"
    spotify_client = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(
        client_id=_SPOTIPY_CLIENT_ID,
        client_secret=_SPOTIPY_CLIENT_SECRET,
        redirect_uri=_SPOTIPY_REDIRECT_URI,
        scope=_SPOTIFY_SCOPE))

    def get_stations() -> List[local_radio.Station]:
        stations = []
        stations.extend(local_radio.create_directory_stations(stations_directory))
        stations.extend(local_radio.create_spotify_stations(spotify_client, _DEVICE_ID))
        return stations

    play_keys = ['a', 's', 'd']
    change_station_previous_keys = ['q', 'w', 'e']
    change_station_next_keys = ['z', 'x', 'c']
    refresh_stations_code = "qwedcxza"
    
    radio = local_radio.Radio(
        get_stations_fn=get_stations,
        play_keys=play_keys,
        change_station_previous_keys=change_station_previous_keys,
        change_station_next_keys=change_station_next_keys,
        refresh_stations_code=refresh_stations_code)
    radio.start()
        
                    
if __name__ == "__main__":
    while True:
        main()
