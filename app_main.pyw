"""
    You will need to pip install:
        pip install PySimpleGUI
        pip install python-vlc
"""
import PySimpleGUI as sg
import os
from sys import platform as PLATFORM
from game_modules.video_player import VideoPlayer
from game_modules.shooter_data import ShooterData

HSG_LOGO_IMG_FILE = "./images/hsg_logo_150px.png"
HSG_LOGO_ICO_FILE = "./images/hsg_logo.ico"
ARCHERY_TARGET_FILE = "./images/archery_target.png"
VIDEO_GAMES_PATH = "./videos"
MAX_PLAYERS = 12

#####################################################################################
## GLOBAL VARS
# Store the game player instance
video_player : VideoPlayer = None
list_selected_games = []
current_game_index: int = 0
# Number of Players
num_of_players: int = 1
current_player_index: int = 0
# Store Player data
shooter_data = ShooterData(MAX_PLAYERS)

#####################################################################################
#------- Fetch available video games ----
def getVideoGameList(video_path: str):
    dir_list = os.scandir(video_path)
    ret_list = []
    for entry in dir_list:
        if entry.is_dir():
            ret_list.append(entry.name)

    return sorted(ret_list)

#####################################################################################
#------- Run videos for each player, game after game
def run_games_for_shooters(first_call: bool):
    all_done = False

    global current_player_index
    global current_game_index
    global video_player
    global list_selected_games
    global num_of_players
    global shooter_data

    if first_call:
        video_player = VideoPlayer(VIDEO_GAMES_PATH)
        current_player_index = 0
        current_game_index = 0

        sg.popup("Bitte bereit machen!",
            "Erster Schütze: {}". format(shooter_data.shooter_by_index(current_player_index)), 
            "-- Taste drücken um zu starten --",
            image = ARCHERY_TARGET_FILE,
            icon = HSG_LOGO_ICO_FILE,
            title = "Willkommen", 
            keep_on_top = True, 
            background_color = 'white', 
            text_color = 'black',
            font = ('Arial', 12, 'bold'),
            any_key_closes = True)
    else:
        current_player_index += 1
        if current_player_index >= num_of_players: 
            current_player_index = 0
            current_game_index += 1
            if current_game_index >= len(list_selected_games):
                all_done = True
        
        if all_done is False:
            sg.popup("BITTE JETZT PFEILE ZIEHEN!",
                "Nächster Schütze: {}". format(shooter_data.shooter_by_index(current_player_index)), 
                "-- Taste drücken um zu starten --",
                image = ARCHERY_TARGET_FILE,
                icon = HSG_LOGO_ICO_FILE,
                title = "Runde beendet", 
                keep_on_top = True, 
                background_color = 'white', 
                text_color = 'black',
                font = ('Arial', 12, 'bold'),
                any_key_closes = True)
        
    if all_done is False:
        # run this player and game        
        video_player.play(shooter_data.shooter_by_index(current_player_index), list_selected_games[current_game_index])
    else:
        sg.popup("BITTE JETZT PFEILE ZIEHEN!",
            "Spiel beendet, danke dass ihr unser Bogen-Kino nutzt!", 
            "-- Taste drücken um zu beenden --",
            image = ARCHERY_TARGET_FILE,
            icon = HSG_LOGO_ICO_FILE,
            title = "Spiel beendet", 
            keep_on_top = True, 
            background_color = 'white', 
            text_color = 'black',
            font = ('Arial', 12, 'bold'),
            any_key_closes = True)
        
        # Shut down the window
        if video_player is not None:
            video_player.stop()
            del video_player
            video_player = None

    return

#####################################################################################
#------- GUI definition & setup --------
# Set Theme
sg.theme('DarkAmber')

#--------- GUI LAYOUT FOR MAIN WINDOW -------------------------------
main_layout = [
    [sg.Push(), sg.Text('HSG - Bogen Kino v0.1'), sg.Push()],
    [sg.Push(), sg.Image(HSG_LOGO_IMG_FILE, size=(150, 150)), sg.Push()],
    [sg.Push(), 
        sg.Text("Verfügbare Spiele", justification = "left"), 
        sg.Push(),
        sg.Text("Ausgewählte Spiele", justification = "right"), 
        sg.Push()],
    [sg.Push(), 
        sg.Listbox(values = getVideoGameList(VIDEO_GAMES_PATH), select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, size = (30,8), key = "-LISTBOX-AVAILABLE-GAMES-", pad = (20,20,0,20)), 
        sg.Listbox(values = [], select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, size = (30,8), key = "-LISTBOX-SELECTED-GAMES-", pad = (20,20,0,20)), 
        sg.Push()],
    [sg.Push(), 
        sg.Button("Alle", size=(10, 1), pad=(1, 1)), 
        sg.Button("->", size=(5, 1), pad=(1, 1)), 
        sg.Push(),
        sg.Button("<-", size=(5, 1), pad=(1, 1)), 
        sg.Button("Leeren", size=(10, 1), pad=(1, 1)), 
        sg.Push()],
    [sg.VPush()],
    [sg.Push(),
        sg.Text("Anzahl Schützen (Mitspieler): "), 
        sg.Button("-", size = (2, 1), pad = (1, 1)), 
        sg.Text("{:02d}".format(num_of_players), key = "-NUM-OF-PLAYER-DISPL-"), 
        sg.Button("+", size = (2, 1), pad = (1, 1)),
        sg.Button("Namen anpassen", size=(15, 1), pad = (50, 1)), 
        sg.Push()],
    [sg.VPush()],
    [sg.Push(), 
        sg.Button("Start", size=(20, 1), pad=(1, 1)),
        sg.Push()],
    [sg.VPush()]
]
################################################################################

### START MAIN Window #############
main_window = sg.Window('HSG Bogen Kino', 
    main_layout, 
    element_justification = 'center', 
    finalize = True, 
    resizable = True, 
    size = (900,600), 
    icon = HSG_LOGO_ICO_FILE)

################################################################################
#------------ The Event Loop ------------#
while True:

    # Get all events and current data from all UI elements
    window, event, values = sg.read_all_windows(timeout = 1000, timeout_key = "__TIMEOUT__")    
   
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break

    if event == "Alle":        
        main_window["-LISTBOX-SELECTED-GAMES-"].update(values = getVideoGameList(VIDEO_GAMES_PATH), set_to_index = 0)
        main_window["-LISTBOX-AVAILABLE-GAMES-"].update(values = [])
        main_window.refresh()

    elif event == "Leeren":
        main_window["-LISTBOX-SELECTED-GAMES-"].update(values = [])
        main_window["-LISTBOX-AVAILABLE-GAMES-"].update(values = getVideoGameList(VIDEO_GAMES_PATH), set_to_index = 0)
        main_window.refresh()
    
    elif event == "->":
        list_available = main_window["-LISTBOX-AVAILABLE-GAMES-"].get_list_values()
        list_selected = main_window["-LISTBOX-SELECTED-GAMES-"].get_list_values()

        if len(list_available) > 0 and len(values["-LISTBOX-AVAILABLE-GAMES-"]) > 0:
            elem = values["-LISTBOX-AVAILABLE-GAMES-"][0]
            list_selected.append(elem)
            list_available.remove(elem)
            main_window["-LISTBOX-SELECTED-GAMES-"].update(values = sorted(list_selected), set_to_index = 0)
            main_window["-LISTBOX-AVAILABLE-GAMES-"].update(values = sorted(list_available), set_to_index = 0)
            main_window.refresh()

    elif event == "<-":
        list_available = main_window["-LISTBOX-AVAILABLE-GAMES-"].get_list_values()
        list_selected = main_window["-LISTBOX-SELECTED-GAMES-"].get_list_values()

        if len(list_selected) > 0 and len(values["-LISTBOX-SELECTED-GAMES-"]) > 0:
            elem = values["-LISTBOX-SELECTED-GAMES-"][0]
            list_available.append(elem)
            list_selected.remove(elem)
            main_window["-LISTBOX-SELECTED-GAMES-"].update(values = sorted(list_selected), set_to_index = 0)
            main_window["-LISTBOX-AVAILABLE-GAMES-"].update(values = sorted(list_available), set_to_index = 0)
            main_window.refresh()
    
    elif event == '+':
        num_of_players = num_of_players + 1
        if num_of_players > MAX_PLAYERS: 
            num_of_players = MAX_PLAYERS
        main_window["-NUM-OF-PLAYER-DISPL-"].update(value = "{:02d}".format(num_of_players))
        main_window.refresh()

    elif event == '-':
        num_of_players = num_of_players - 1
        if num_of_players < 1: 
            num_of_players = 1
        main_window["-NUM-OF-PLAYER-DISPL-"].update(value = "{:02d}".format(num_of_players))
        main_window.refresh()

    elif event == 'Namen anpassen':
        shooter_data.configure(num_of_players)

    elif event == 'Start':
        list_selected_games = main_window["-LISTBOX-SELECTED-GAMES-"].get_list_values()
        if len(list_selected_games) > 0:
            run_games_for_shooters(True)

    ## This is an event from the shooter configuration window
    elif event == "Spieler OK":
        shooter_data.close_config_win()

    ## THIS IS AN EVENT FROM THE PLAYER WINDOW:
    elif event == 'Abbrechen':
        if (video_player is not None):
            video_player.stop()
            del video_player
            video_player = None
    
    ## Allow the player window to update the time 
    if (video_player is not None):
        vid_done = video_player.update_time()
        if (vid_done is True):
            run_games_for_shooters(False)

################################################################################
## CLEAN UP
main_window.close()