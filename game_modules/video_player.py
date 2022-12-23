import PySimpleGUI as sg
import vlc
import os
from sys import platform as PLATFORM
import random
import time

###
# VLC LIB Docu: https://www.olivieraubert.net/vlc/python-ctypes/doc/

class VideoPlayer:
    screen_width: int
    screen_height: int
    video_file: str
    video_path: str
    video_started: bool
    play_window: None
    play_win_layout: None
    vlc_inst: None
    vlc_player: None

    ##############################################################################################################
    def __init__(self, video_path: str):
        ## fill variables
        self.video_path = video_path
        self.video_started = False
        
        ## get size of screen
        self.screen_width, self.screen_height = sg.Window.get_screen_size()
        print("Screen Size: {} x {}".format(self.screen_width, self.screen_height))

        ## setup window layout
        video_width : int = self.screen_width
        video_height : int  = (self.screen_height * 0.85)
        print("Video Size: {} x {}".format(video_width, video_height))

        self.play_win_layout = [
            [sg.Push(background_color = 'yellow'), sg.Button('Abbrechen')],
            [sg.Text('Schütze: ', background_color = 'black', font = ('arial', 18, 'bold')), 
                sg.Text("Hawkeye", key='-PLAYER-NAME-', background_color = 'black', text_color = 'red', font = ('arial', 18, 'bold')),
                sg.Push(background_color = 'black'),
                sg.Text('Zeit: ', background_color = 'black'), sg.Text('--:--', key='-TIME-DISPLAY-', background_color = 'black')
            ],
            [sg.Image('', size = (video_width, video_height), key='-VIDEO-OUT-')]
        ]

        ## Setup VLC Player
        self.vlc_inst = vlc.Instance()
        self.vlc_player = self.vlc_inst.media_player_new()
        
        ## Start Window
        self.play_window = sg.Window('HSG Bogen Kino Player', 
            self.play_win_layout, 
            element_justification = 'left', 
            finalize = True, 
            resizable = False,
            location = (0, 0),
            size = (self.screen_width, self.screen_height),
            background_color = "black",
            no_titlebar = True,
            keep_on_top = True,
            modal = True
        )

        # Give some time for the window to come up
        time.sleep(1)

        # Assing VLC the window to play in
        self.play_window['-VIDEO-OUT-'].expand(True, True) 
        if PLATFORM.startswith('linux'):
            self.vlc_player.set_xwindow(self.play_window['-VIDEO-OUT-'].Widget.winfo_id())
        else:
            self.vlc_player.set_hwnd(self.play_window['-VIDEO-OUT-'].Widget.winfo_id())       


    ##############################################################################################################
    def collect_playlist_files(self, game_name: str):
        path = self.video_path + "/" + game_name
        file_list = os.listdir(path)

        # pick one out of the found files
        random.shuffle(file_list)
        for file in file_list:
            if file.endswith('.mp4'):
                self.video_file = path + "/" + file
                break

        print("Video file selected for this game: {}".format(self.video_file))
        return

    ##############################################################################################################
    def play(self, shooter_name: str, game_name: str):

        print("Player {} is now playing game {}.".format(shooter_name, game_name))

        # Collect, shuffle and select one video from the game folder
        self.collect_playlist_files(game_name)

        # Load the video
        media = self.vlc_inst.media_new_path(self.video_file)
        self.vlc_player.set_media(media)

        # Update the shooter name
        self.play_window["-PLAYER-NAME-"].update(value = shooter_name)
        self.play_window.refresh()

        # Play the video and give some time for the buffering
        self.vlc_player.play()
        time.sleep(1)
        self.video_started = True

        return
    
    ##############################################################################################################
    def stop(self):
        self.video_started = False
        self.vlc_player.stop()
        self.play_window.close()
        del self.play_window
        self.play_window = None

        return
    
    ##############################################################################################################
    def update_time(self) -> bool: # returns true when video is finished
        if self.video_started is True:
            if self.vlc_player.is_playing():
                remaining_time_msec: int = self.vlc_player.get_length() - self.vlc_player.get_time()
                self.play_window['-TIME-DISPLAY-'].update("{:02d}:{:02d}".format(*divmod(remaining_time_msec//1000, 60)))
                return False
            else:    
                return True
        else:
            return False
