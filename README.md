# local-radio

The local radio plays stations defined by directories full of audio files. The current track and time position within a station playlist is determined by the current time so stations "keep playing" even when you have switched away, a la the actual radio.

# Set Up
Recommend using python 3.9.

Install VLC.

```pip install -r requirements.txt```

Create a parent directory to contain your stations. Each directory in the parent directory is a station. Within each station, store 1-many audio files as the playlist for that station. The files will be sorted lexicographically by name to form the station playlist. 

Modify local_radio.py to point to the directory containing the station folders.

Update ```play_keys```, ```previous_station_keys```, and ```next_station_keys``` appropriately based on your input mechanism of choice. The play keys are used to toggle play/pause. The previous and next stations keys seek between stations, which are also ordered lexicographically by station directory name.

Run 

```$ python local_radio.py```
