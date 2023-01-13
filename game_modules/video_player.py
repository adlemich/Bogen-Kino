import PySimpleGUI as sg
import vlc
import os
from sys import platform as PLATFORM
import random
import time
from datetime import datetime

################################################################################################
# VLC LIB Docu: https://www.olivieraubert.net/vlc/python-ctypes/doc/
# PySimpleGui Docu: https://www.pysimplegui.org/en/latest/call%20reference/ 
################################################################################################

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
        sg.cprint("{} - TRACE: Initializing class {}.".format(datetime.now(), self.__class__))

        ## fill variables
        self.video_path = video_path
        self.video_started = False
        
        ## get size of screen
        self.screen_width, self.screen_height = sg.Window.get_screen_size()
        sg.cprint("{} - Screen Size: {} x {}".format(datetime.now(), self.screen_width, self.screen_height))

        ## setup window layout
        video_width : int = self.screen_width
        video_height : int  = (self.screen_height * 0.85)
        sg.cprint("{} - Video Size: {} x {}".format(datetime.now(), video_width, video_height))

        self.play_win_layout = [
            [sg.ProgressBar(max_value = 1, orientation = "horizontal", expand_x = True, bar_color = ('green','green'), size_px = (1, 5), key = "-PLAYER-TOP-LINE-")],
            [sg.Text('Schütze: ', background_color = 'black', text_color = 'white', font = ('arial', 18, 'bold')), 
                sg.Text("Hawkeye", key='-PLAYER-NAME-', background_color = 'black', text_color = 'red', font = ('arial', 18, 'bold')),
                sg.Push(background_color = 'black'),
                sg.Text('Zeit: ', background_color = 'black', text_color = 'white'), sg.Text('--:--', key='-TIME-DISPLAY-', background_color = 'black', text_color = 'white')
            ],
            [sg.Image('', size = (video_width, video_height), key='-VIDEO-OUT-')],
            [sg.ProgressBar(max_value = 1, orientation = "horizontal", expand_x = True, bar_color = ('green','green'), size_px = (1, 5), key = "-PLAYER-BOTTOM-LINE-")],
            #[sg.Button('Schuss', focus = True, expand_x = True, bind_return_key = True, key = "-BUTTON_BANG-", border_width = 0, button_color = "white on black")]
            [sg.Button('Schuss', focus = True, expand_x = True, border_width = 0, button_color = "white on black", key = "-BUTTON-SCHUSS-"), sg.Button('Abbrechen')]
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
            keep_on_top = False,
            modal = False
        )

        # Give some time for the window to come up
        time.sleep(1)

        # Assing VLC the window to play in
        self.play_window['-VIDEO-OUT-'].expand(True, True) 
        if PLATFORM.startswith('linux'):
            self.vlc_player.set_xwindow(self.play_window['-VIDEO-OUT-'].Widget.winfo_id())
        else:
            self.vlc_player.set_hwnd(self.play_window['-VIDEO-OUT-'].Widget.winfo_id())       

        # Fill upper and lower Progress Bar
        self.play_window["-PLAYER-TOP-LINE-"].update(current_count = 1, bar_color = ("green","green"))  
        self.play_window["-PLAYER-BOTTOM-LINE-"].update(current_count = 1, bar_color = ("green","green"))

        # Set focus to bang Button
        self.play_window["-BUTTON-SCHUSS-"].set_focus()

        return

    ##############################################################################################################
    def collect_playlist_files(self, game_name: str):
        sg.cprint("{} - TRACE: {}.collect_playlist_files()".format(datetime.now(), self.__class__))

        path = self.video_path + "/" + game_name
        file_list = os.listdir(path)

        # pick one out of the found files
        random.shuffle(file_list)
        for file in file_list:
            if file.endswith('.mp4'):
                self.video_file = path + "/" + file
                break

        sg.cprint("{} - Video file selected for this game: {}".format(datetime.now(), self.video_file))
        return

    ##############################################################################################################
    def play(self, shooter_name: str, game_name: str):
        sg.cprint("{} - TRACE: {}.play()".format(datetime.now(), self.__class__))

        sg.cprint("{} - Player {} is now playing game {}.".format(datetime.now(), shooter_name, game_name))

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
        self.vlc_player.audio_set_volume(50)
        time.sleep(1)
        self.video_started = True

        return
    
    ##############################################################################################################
    def stop(self):
        sg.cprint("{} - TRACE: {}.stop()".format(datetime.now(), self.__class__))

        self.video_started = False
        self.vlc_player.stop()
        self.vlc_player.release()
        self.vlc_inst.release()
        self.play_window.close()
        self.play_window = None

        return
    
    ##############################################################################################################
    def update_time(self) -> bool: # returns true when video is finished
        #sg.cprint("{} - TRACE: {}.update_time()".format(datetime.now(), self.__class__))  # no tracing, to noisy

        if self.video_started is True:
            if self.vlc_player.is_playing():
                remaining_time_msec: int = self.vlc_player.get_length() - self.vlc_player.get_time()
                self.play_window['-TIME-DISPLAY-'].update("{:02d}:{:02d}".format(*divmod(remaining_time_msec//1000, 60)))
                return False
            else:    
                return True
        else:
            return False

    ##############################################################################################################
    def pause(self):
        sg.cprint("{} - TRACE: {}.pause()".format(datetime.now(), self.__class__))

        if self.video_started is True:
            sg.cprint("{} - Pausing video play....".format(datetime.now()))
            self.vlc_player.pause()
            self.play_window['-TIME-DISPLAY-'].update(background_color = 'white', text_color = 'black')  
            self.play_window["-PLAYER-TOP-LINE-"].update(current_count = 1, bar_color = ("red","red"))  
            self.play_window["-PLAYER-BOTTOM-LINE-"].update(current_count = 1, bar_color = ("red","red"))             
            self.play_window.refresh()
        return

    ##############################################################################################################
    def resume(self):
        sg.cprint("{} - TRACE: {}.resume()".format(datetime.now(), self.__class__))

        if self.video_started is True:
            sg.cprint("{} - Resuming video play....".format(datetime.now()))
            self.vlc_player.pause()
            self.play_window['-TIME-DISPLAY-'].update(background_color = 'black', text_color = 'white')
            self.play_window["-PLAYER-TOP-LINE-"].update(current_count = 1, bar_color = ("green","green"))  
            self.play_window["-PLAYER-BOTTOM-LINE-"].update(current_count = 1, bar_color = ("green","green"))
            self.play_window.refresh()
        return