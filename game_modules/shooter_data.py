import PySimpleGUI as sg
from typing import List

class ShooterData:
    config_window: None
    config_layout: None
    max_players: int
    num_of_players: int
    current_player_index: int
    player_names: List[str]
    

    ##############################################################################################################
    def __init__(self, max_players: int):
        self.max_players = max_players
        self.num_of_players = 1
        self.current_player_index = 0
        
        self.player_names = ["Hawkeye"]        
        for i in range(1, self.max_players):
            self.player_names.append("???-{:02d}".format(i + 1))
        
        return        

    ##############################################################################################################
    def configure(self, num_of_players: int) -> sg.Window:

        if (num_of_players > self.max_players):
            self.num_of_players = self.max_players
        else:
            self.num_of_players = num_of_players

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

        self.config_window = sg.Window('HSG Bogen Kino Player - Spieler Einstellungen', 
            self.config_layout, 
            element_justification = 'left', 
            finalize = True, 
            resizable = False,
            size = (400, win_height),
            modal = True
        )
        return self.config_window

    ##############################################################################################################
    def close_config_win(self):

        self.config_window.read(timeout = 1, timeout_key = "__TIMEOUT__")  

        for i in range(self.num_of_players):
            key_name = "-PLAYER_{:02d}_NAME-".format(i)
            self.player_names[i] = self.config_window[key_name].get()

        self.config_window.close()
        self.config_window = None
        return

    ##############################################################################################################
    def next_shooter(self):
        self.current_player_index = self.current_player_index + 1
        if self.current_player_index > (self.num_of_players - 1):
            self.current_player_index = 0

        return self.player_names[self.current_player_index]

    ##############################################################################################################
    def current_shooter(self):
        return self.player_names[self.current_player_index]
    ##############################################################################################################
    def get_shooters(self):
        return self.player_names
    ##############################################################################################################
    def shooter_by_index(self, index: int):
        return self.player_names[index]