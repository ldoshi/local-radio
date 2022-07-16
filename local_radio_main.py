import local_radio

def main():
    stations_directory = "/home/lyric/Documents/local-radio/stations"
    directory_stations = local_radio.create_directory_stations(stations_directory)

    stations = directory_stations
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
