import requests
import vlc
import tkinter as tk

from tkinter import ttk


RECORD_API = "https://radiorecord.ru/api"
RECORD_API_STATIONS = f"{RECORD_API}/stations/"
RECORD_API_NOW = f"{RECORD_API}/stations/now/"

GUI_WINDOW_WIDTH = 400
GUI_WINDOW_HEIGHT = 100
GUI_WINDOW_X = 1100
GUI_WINDOW_Y = 200

# define VLC instance
instance = vlc.Instance("--input-repeat=-1", "--fullscreen")

# Define VLC player
player = instance.media_player_new()


def request_track(stations, label_track):
    def wrapper(eventObject):
        label_track["text"] = ""

        # Поиск станции по названию.
        station = None
        for st in stations:
            if st.get("title") == eventObject.widget.get():
                station = st
                break

        if station != None:
            # Запрос текущих треков на станциях.
            response = requests.get(RECORD_API_NOW)

            tracks_json = response.json()
            tracks = tracks_json.get("result")

            # Поиск трека по идентификатору станции.
            track = None
            for tr in tracks:
                if tr.get("id") == station.get("id"):
                    track = tr.get("track")
                    break

            if track != None:
                artist = track["artist"]
                song = track["song"]

                label_track["text"] = f"{artist} - {song}"

            # Define VLC media
            media = instance.media_new(station.get("stream_320"))

            # Set player media
            player.set_media(media)

            # Play the media
            player.play()

    return wrapper


def main():
    gui = tk.Tk()

    gui.config(bg="white")
    gui.title("Radio Record Now")
    gui.geometry(
        f"{GUI_WINDOW_WIDTH}x{GUI_WINDOW_HEIGHT}+{GUI_WINDOW_X}+{GUI_WINDOW_Y}"
    )
    gui.minsize(300, 100)
    gui.maxsize(500, 500)
    gui.resizable(True, True)

    # Запрос всех жанров и станций.
    response = requests.get(RECORD_API_STATIONS)

    stations_json = response.json()  # преобразование json в словарь (dict)
    stations_result = stations_json.get("result")
    stations = stations_result.get("stations")

    stations_count = len(stations)
    tk.Label(gui, text=f"Количество станций: {stations_count}").pack()

    genres_count = len(stations_result.get("genre"))
    tk.Label(gui, text=f"Количество жанров: {genres_count}").pack()

    stations_list = []
    for st in stations:
        stations_list.append(st.get("title"))

    label_track = tk.Label(gui, text="")
    label_track.pack()

    comb_stations = ttk.Combobox(gui, values=stations_list, state="readonly")

    comb_stations.bind("<<ComboboxSelected>>", request_track(stations, label_track))

    comb_stations.pack()

    gui.mainloop()


# with open("table.csv", "w") as f:
#     f.write("Artist,Song\n")
#     f.write(f"{artist},{song}\n")

if __name__ == "__main__":
    main()
