import PySimpleGUI as sg
from typing import List
from datetime import datetime

class ShooterData:
       
    ##############################################################################################################
    def __init__(self, max_players: int):        
        sg.cprint("{} - TRACE: Initializing class {}.".format(datetime.now(), self.__class__))

        self.max_players = max_players
        self.num_of_players = 1
        self.player_names = ["Hawkeye"]       
                
        self.config_layout = None
        self.config_window = None

        return        

    ##############################################################################################################
    def configure(self, num_of_players: int) -> sg.Window:
        sg.cprint("{} - TRACE: {}.configure()".format(datetime.now(), self.__class__))

        if (num_of_players > self.max_players):
            self.num_of_players = self.max_players
        else:
            self.num_of_players = num_of_players

        # Pre-fill the names
        self.player_names.clear()
        for i in range(0, self.num_of_players):
            self.player_names.append("XYZ-{:02d}".format(i + 1))

        self.config_layout = [
            [sg.VPush()],
            [sg.Text('Spieler 01: '), sg.InputText(self.player_names[0], key = "-PLAYER_00_NAME-")]
        ]

        if (self.num_of_players > 1):
            for i in range (2, self.num_of_players + 1):
                self.config_layout.append([sg.Text("Spieler {:02d}: ".format(i)), sg.InputText(self.player_names[i-1], key = "-PLAYER_{:02d}_NAME-".format(i-1))])

        self.config_layout.append([sg.VPush()])
        self.config_layout.append([sg.Button("Spieler OK", size = (20, 1), pad = (1, 1))])
        self.config_layout.append([sg.VPush()])

        win_height = 100 + (self.num_of_players * 30)

        self.config_window = sg.Window('HSG Bogen Kino - Spieler Einstellungen', 
            self.config_layout, 
            element_justification = 'left', 
            finalize = True, 
            resizable = False,
            size = (400, win_height),
            modal = True,
            disable_close = True,
            disable_minimize = True
        )
        return self.config_window

    ##############################################################################################################
    def close_config_win(self):
        sg.cprint("{} - TRACE: {}.close_config_win()".format(datetime.now(), self.__class__))

        self.config_window.read(timeout = 1, timeout_key = "__TIMEOUT__")  

        for i in range(self.num_of_players):
            key_name = "-PLAYER_{:02d}_NAME-".format(i)
            self.player_names[i] = self.config_window[key_name].get()

        self.config_window.close()
        self.config_window = None
        return

    ##############################################################################################################
    def get_shooters(self):
        sg.cprint("{} - TRACE: {}.get_shooters()".format(datetime.now(), self.__class__))

        return self.player_names
    ##############################################################################################################
    def shooter_by_index(self, index: int):
        sg.cprint("{} - TRACE: {}.shooter_by_index()".format(datetime.now(), self.__class__))

        return self.player_names[index]