import local_radio
import spotipy

# Spotify access.
_SPOTIPY_CLIENT_ID='5b235f6968d5493db1dbda0e5f306f1a'
_SPOTIPY_CLIENT_SECRET='8773a9fa89684e768883bfa733ab7875'
_SPOTIPY_REDIRECT_URI='http://localhost'
_SPOTIFY_SCOPE = ["user-modify-playback-state", "user-read-playback-state", "user-read-currently-playing", "playlist-read-private", "playlist-read-collaborative", "app-remote-control", "streaming", "user-library-read"]

# lemmings player.
_DEVICE_ID = "a582ca56f0f370cf4eae00f3f1fccaad174b15bb"


def main():
    stations_directory = "/home/lyric/Documents/local-radio/stations"
    directory_stations = local_radio.create_directory_stations(stations_directory)

    spotify_client = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(
        client_id=_SPOTIPY_CLIENT_ID,
        client_secret=_SPOTIPY_CLIENT_SECRET,
        redirect_uri=_SPOTIPY_REDIRECT_URI,
        scope=_SPOTIFY_SCOPE))
    spotify_stations = local_radio.create_spotify_stations(spotify_client, _DEVICE_ID)

    stations = directory_stations + spotify_stations
    play_keys = ['a', 's', 'd']
    change_station_previous_keys = ['q', 'w', 'e']
    change_station_next_keys = ['z', 'x', 'c']

    radio = local_radio.Radio(
        stations=stations,
        play_keys=play_keys,
        change_station_previous_keys=change_station_previous_keys,
        change_station_next_keys=change_station_next_keys)
    radio.start()
                    
if __name__ == "__main__":
    main()
