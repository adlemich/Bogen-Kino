import PySimpleGUI as sg
import os
from datetime import datetime
import time
from sys import platform as PLATFORM
from game_modules.app_configuration import AppConfig
from game_modules.video_player import VideoPlayer
from game_modules.shooter_data import ShooterData
from game_modules.audio_bang_detector import BangDetector
from game_modules.camera_control import CameraControl
from game_modules.result_processor import ResultProcessor

################################################################################################
# PySimpleGui Docu: https://www.pysimplegui.org/en/latest/call%20reference/ 
################################################################################################

class GameEngine:

    #####################################################################################
    #------- INIT
    def __init__(self):        
        sg.cprint("{} - TRACE: Initializing class {}.".format(datetime.now(), self.__class__))

        # Init helper classes
        self.video_player : VideoPlayer = None
        self.shooter_data = ShooterData(AppConfig.CFG_MAX_PLAYERS)
        self.bang_detector = BangDetector()
        self.webcam_handler = CameraControl()
        self.result_processor = ResultProcessor()

        # Runtime data
        self.session_id = ""
        self.current_game_index = 0
        self.timeout_count = 0
        self.game_active = False
        self.list_selected_games = []   
        
        # Number of Players
        self.num_of_players = 1
        self.current_player_index = 0
        self.current_player_arrow_nr = 1
        
        #--------- SETUP GUI LAYOUT FOR MAIN WINDOW -------------------------------
        options_menu_def = [
            ['Hilfe', ['App Info']],
            ['Einstellungen', ['Kamera', 'Mikrofon', 'Farben']],
            ['Debugger', ['Einblenden', 'Ausblenden']]
        ]

        self.main_layout = [
            [sg.MenubarCustom(options_menu_def, background_color = sg.theme_background_color(), text_color = sg.theme_text_color(), bar_background_color = sg.theme_background_color(), bar_text_color = sg.theme_text_color())],
            [sg.Push(), sg.Text('HSG - Bogen Kino {}'.format(AppConfig.CFG_VERSION), font = ("Times", 18, "bold")), sg.Push()],
            [sg.Push(), sg.Image(AppConfig.CFG_HSG_LOGO_IMG_FILE, size=(150, 150)), sg.Push()],
            [sg.Push(), 
                sg.Text("Verfügbare Spiele", justification = "left"), 
                sg.Push(),
                sg.Text("Ausgewählte Spiele", justification = "right"), 
                sg.Push()],
            [sg.Push(), 
                sg.Listbox(values = self.getVideoGameList(), select_mode = sg.LISTBOX_SELECT_MODE_SINGLE, size = (30,8), key = "-LISTBOX-AVAILABLE-GAMES-", pad = (20,20,0,20)), 
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
                sg.Text("{:02d}".format(self.num_of_players), key = "-NUM-OF-PLAYER-DISPL-"), 
                sg.Button("+", size = (2, 1), pad = (1, 1)),
                sg.Button("Namen anpassen", size=(15, 1), pad = (50, 1)), 
                sg.Push()],
            [sg.VPush()],
            [sg.Push(), 
                sg.Button("Start", size=(20, 1), pad=(1, 1)),
                sg.Push()],
            [sg.VPush()]
        ]

        ### START MAIN Window #############
        self.main_window = sg.Window('HSG Bogen Kino', 
            self.main_layout, 
            element_justification = 'center', 
            finalize = True, 
            resizable = True, 
            size = (900,600), 
            icon = AppConfig.CFG_HSG_LOGO_ICO_FILE,
            metadata = "main")

        return

    #####################################################################################
    #------- Fetch available video games ----
    def getVideoGameList(self):
        sg.cprint("{} - TRACE: {}.getVideoGameList()".format(datetime.now(), self.__class__))

        dir_list = os.scandir(AppConfig.CFG_VIDEO_GAMES_PATH)
        ret_list = []
        for entry in dir_list:
            if entry.is_dir():
                ret_list.append(entry.name)

        return sorted(ret_list)

    #####################################################################################
    #------- Open image viewer app
    def open_image_viewer(self):
        sg.cprint("{} - TRACE: {}.open_image_viewer()".format(datetime.now(), self.__class__))

        image_path = self.webcam_handler.get_last_image_path()
        image_path = image_path.replace("/", "\\")
        os.startfile(filepath = image_path)

        return

    #####################################################################################
    #------- Run videos for each player, game after game
    def run_games_for_shooters(self, first_call: bool):
        #sg.cprint("{} - TRACE: {}.run_games_for_shooters()".format(datetime.now(), self.__class__)) ## no tracing, to noisy

        all_done = False

        if first_call:
            # Init the result class   
            self.result_processor.clear_results()
            self.result_processor.init_session_results(
                self.shooter_data.get_shooters(), 
                self.list_selected_games, 
                self.session_id,
                "{}/{}".format(AppConfig.CFG_CAM_PICTURE_STORAGE_PATH, self.session_id), 
                "{}/{}".format(AppConfig.CFG_RESULTS_STORAGE_PATH, self.session_id)
            )

            sg.cprint("{} - Starting Video Player and get going....".format(datetime.now()))

            self.video_player = VideoPlayer(AppConfig.CFG_VIDEO_GAMES_PATH)
            self.current_player_index = 0
            self.current_game_index = 0

            sg.popup("Bitte bereit machen!",
                "Erster Schütze: {}". format(self.shooter_data.shooter_by_index(self.current_player_index)), 
                "Du brauchst {} Pfeile - es werden nur die ersten {} Pfeile gewertet, auch wenn du mehr schiesst.".format(AppConfig.CFG_ARROWS_PER_PLAYER, AppConfig.CFG_ARROWS_PER_PLAYER),
                "-- Taste drücken um zu starten --",
                image = AppConfig.CFG_ARCHERY_TARGET_FILE,
                icon = AppConfig.CFG_HSG_LOGO_ICO_FILE,
                title = "Willkommen", 
                keep_on_top = True, 
                font = ('Arial', 12, 'bold'),
                any_key_closes = True)
        else:
            sg.cprint("{} - Shooter {} is done, moving to next shooter...".format(datetime.now(), self.current_player_index))
            self.current_player_index += 1
            self.current_player_arrow_nr = 1
            
            if self.current_player_index >= self.num_of_players: 
                sg.cprint("{} - Game {} is done, moving to first shooter for next game...".format(datetime.now(), self.current_game_index))
                self.current_player_index = 0
                self.current_game_index += 1
                if self.current_game_index >= len(self.list_selected_games):
                    sg.cprint("{} - All shooters have done all games. Finishing it off...".format(datetime.now()))
                    all_done = True
            
            if all_done is False:
                sg.popup("BITTE JETZT PFEILE ZIEHEN!",
                    "Nächster Schütze: {}". format(self.shooter_data.shooter_by_index(self.current_player_index)), 
                    "-- Taste drücken um zu starten --",
                    image = AppConfig.CFG_ARCHERY_TARGET_FILE,
                    icon = AppConfig.CFG_HSG_LOGO_ICO_FILE,
                    title = "Runde beendet", 
                    keep_on_top = True, 
                    font = ('Arial', 12, 'bold'),
                    any_key_closes = True)
            
        if all_done is False:
            # run this player and game     
            sg.cprint("{} - Starting game {} for shooter {}...".format(datetime.now(), self.current_game_index, self.current_player_index))               
            self.video_player.play(self.shooter_data.shooter_by_index(self.current_player_index), self.list_selected_games[self.current_game_index])
            self.game_active = True
        else:
            self.game_active = False
            sg.cprint("{} - All done, shutting down video player...".format(datetime.now()))   

            # Shut down the player window
            if self.video_player is not None:
                self.video_player.stop()
                del self.video_player
                self.video_player = None            

            # Show Popup
            sg.popup("BITTE JETZT PFEILE ZIEHEN!",
                "Spiel beendet, danke dass ihr unser Bogen-Kino nutzt!", 
                "-- Taste drücken um die Bilder manuell auszuwerten und Resultate anzuzeigen --",
                image = AppConfig.CFG_ARCHERY_TARGET_FILE,
                icon = AppConfig.CFG_HSG_LOGO_ICO_FILE,
                title = "Spiel beendet", 
                keep_on_top = True, 
                font = ('Arial', 12, 'bold'),
                any_key_closes = True)
            
            # Run a image viewer to check out the latest web-cam images
            self.result_processor.show_result_window()
            #self.open_image_viewer()
                
        return

    #####################################################################################
    #------- Button "Alle"
    def on_button_alle(self):
        sg.cprint("{} - TRACE: {}.on_button_alle()".format(datetime.now(), self.__class__))

        self.main_window["-LISTBOX-SELECTED-GAMES-"].update(values = self.getVideoGameList(), set_to_index = 0)
        self.main_window["-LISTBOX-AVAILABLE-GAMES-"].update(values = [])
        self.main_window.refresh()
        return

    #####################################################################################
    #------- Button "Leeren"
    def on_button_leeren(self):
        sg.cprint("{} - TRACE: {}.on_button_leeren()".format(datetime.now(), self.__class__))

        self.main_window["-LISTBOX-SELECTED-GAMES-"].update(values = [])
        self.main_window["-LISTBOX-AVAILABLE-GAMES-"].update(values = self.getVideoGameList(), set_to_index = 0)
        self.main_window.refresh()
        return

    #####################################################################################
    #------- Button "->"
    def on_button_nachrechts(self, values):
        sg.cprint("{} - TRACE: {}.on_button_nachrechts()".format(datetime.now(), self.__class__))

        list_available = self.main_window["-LISTBOX-AVAILABLE-GAMES-"].get_list_values()
        list_selected = self.main_window["-LISTBOX-SELECTED-GAMES-"].get_list_values()

        if len(list_available) > 0 and len(values["-LISTBOX-AVAILABLE-GAMES-"]) > 0:
            elem = values["-LISTBOX-AVAILABLE-GAMES-"][0]
            list_selected.append(elem)
            list_available.remove(elem)
            self.main_window["-LISTBOX-SELECTED-GAMES-"].update(values = sorted(list_selected), set_to_index = 0)
            self.main_window["-LISTBOX-AVAILABLE-GAMES-"].update(values = sorted(list_available), set_to_index = 0)
            self.main_window.refresh()

        return

    #####################################################################################
    #------- Button "<-"
    def on_button_nachlinks(self, values):
        sg.cprint("{} - TRACE: {}.on_button_nachlinks()".format(datetime.now(), self.__class__))

        list_available = self.main_window["-LISTBOX-AVAILABLE-GAMES-"].get_list_values()
        list_selected = self.main_window["-LISTBOX-SELECTED-GAMES-"].get_list_values()

        if len(list_selected) > 0 and len(values["-LISTBOX-SELECTED-GAMES-"]) > 0:
            elem = values["-LISTBOX-SELECTED-GAMES-"][0]
            list_available.append(elem)
            list_selected.remove(elem)
            self.main_window["-LISTBOX-SELECTED-GAMES-"].update(values = sorted(list_selected), set_to_index = 0)
            self.main_window["-LISTBOX-AVAILABLE-GAMES-"].update(values = sorted(list_available), set_to_index = 0)
            self.main_window.refresh()

        return

    #####################################################################################
    #------- Button "+"
    def on_button_mehr(self):
        sg.cprint("{} - TRACE: {}.on_button_mehr()".format(datetime.now(), self.__class__))

        self.num_of_players += 1
        if self.num_of_players > AppConfig.CFG_MAX_PLAYERS: 
            self.num_of_players = AppConfig.CFG_MAX_PLAYERS
        self.main_window["-NUM-OF-PLAYER-DISPL-"].update(value = "{:02d}".format(self.num_of_players))
        self.main_window.refresh()

        return

    #####################################################################################
    #------- Button "-"
    def on_button_weniger(self):
        sg.cprint("{} - TRACE: {}.on_button_weniger()".format(datetime.now(), self.__class__))

        self.num_of_players -= 1
        if self.num_of_players < 1: 
            self.num_of_players = 1
            self.shooter_data.num_of_players = 1
        self.main_window["-NUM-OF-PLAYER-DISPL-"].update(value = "{:02d}".format(self.num_of_players))
        self.main_window.refresh()

        return

    #####################################################################################
    #------- Button "Namen anpassen"
    def on_button_namenanpassen(self):
        sg.cprint("{} - TRACE: {}.on_button_namenanpassen()".format(datetime.now(), self.__class__))

        self.shooter_data.configure(self.num_of_players)
        return

    #####################################################################################
    #------- Button "Namen anpassen OK"
    def on_button_namenanpassen_ok(self):
        sg.cprint("{} - TRACE: {}.on_button_namenanpassen_ok()".format(datetime.now(), self.__class__))

        self.shooter_data.close_config_win()
        return

    #####################################################################################
    #------- Button "Start"
    def on_button_start(self):
        sg.cprint("{} - TRACE: {}.on_button_start()".format(datetime.now(), self.__class__))

        # setup a session ID
        ct = datetime.now()
        self.session_id = "BogenKino_{:04d}-{:02d}-{:02d}_{:02d}-{:02d}".format(ct.year, ct.month, ct.day, ct.hour, ct.minute)

        # Get selected games and run it
        self.list_selected_games = self.main_window["-LISTBOX-SELECTED-GAMES-"].get_list_values()
        if len(self.list_selected_games) > 0:
            self.run_games_for_shooters(True)
        else:
            sg.popup_ok("Bitte wähle mindestens 1 Spiel aus (in die rechte Box verschieben mit -> oder Alle.")
        return

    #####################################################################################
    #------- Button "Abbrechen" - from the video player window
    def on_button_player_abbrechen(self):
        sg.cprint("{} - TRACE: {}.on_button_player_abbrechen()".format(datetime.now(), self.__class__))

        if (self.video_player is not None):
            self.video_player.stop()
            del self.video_player
            self.video_player = None
        return

    #####################################################################################
    #------- Button "Microphone" - from the settings menu
    def on_menu_setting_micro(self):
        sg.cprint("{} - TRACE: {}.on_menu_setting_micro()".format(datetime.now(), self.__class__))

        if (self.bang_detector is not None):
            self.bang_detector.configure()
        return

    #####################################################################################
    #------- Button "Microphone OK" - from the configuration dialog
    def on_button_micro_ok(self):
        sg.cprint("{} - TRACE: {}.on_button_micro_ok()".format(datetime.now(), self.__class__))

        if (self.bang_detector is not None):
            self.bang_detector.close_config_win()
        return

    #####################################################################################
    #------- Button "Camera" - from the settings menu
    def on_menu_setting_camera(self):
        sg.cprint("{} - TRACE: {}.on_menu_setting_camera()".format(datetime.now(), self.__class__))

        if (self.webcam_handler is not None):
            self.webcam_handler.configure()
        return

    #####################################################################################
    #------- Button "Camera OK" - from the configuration dialog
    def on_button_camera_ok(self):
        sg.cprint("{} - TRACE: {}.on_button_camera_ok()".format(datetime.now(), self.__class__))

        if (self.webcam_handler is not None):
            self.webcam_handler.close_config_win()
        return

    #####################################################################################
    #------- Button "!! BANG !!" - from the video player 
    def on_button_bang(self):
        sg.cprint("{} - TRACE: {}.on_button_bang()".format(datetime.now(), self.__class__))

        sg.cprint("{} - BANG !!! Manual via Keyboard - will now take a shot with the camera!".format(datetime.now()))
        self.handle_bang()
        return

    #####################################################################################
    #------- Check the video if still playing and update the window with time info
    def on_event_loop_timeout(self):
        #sg.cprint("{} - TRACE: {}.on_event_loop_timeout()".format(datetime.now(), self.__class__))   # not tracing, to noisy

        self.timeout_count += 1
        if self.timeout_count >= ((1000 / AppConfig.CFG_CYCLE_TIMEOUT_MS) - 1):
            ## Allow the player window to update the time every one second
            if (self.video_player is not None):
                self.vid_done = self.video_player.update_time()
                if (self.vid_done is True):
                    self.run_games_for_shooters(False)
            self.timeout_count = 0

        ## Listen for impact via audio detection
        if self.game_active is True:
            if self.bang_detector.listen() is True:
                sg.cprint("{} - BANG !!! Impact via AUDIO detected - will now take a shot with the camera!".format(datetime.now()))
                self.handle_bang()
                
        return

    #####################################################################################
    #------- Pause the video and take a shot with the camera when a bang was detected, but only for the 3 first arrows
    def handle_bang(self):
        sg.cprint("{} - TRACE: {}.handle_bang()".format(datetime.now(), self.__class__)) 

        # check the amount of arrows
        if self.current_player_arrow_nr > AppConfig.CFG_ARROWS_PER_PLAYER:
            sg.cprint("{} - TRACE: Will skip this BANG!!, shooter already has {} arrow pictures recorded.".format(datetime.now(), AppConfig.CFG_ARROWS_PER_PLAYER)) 
            return

        # pause the video, and take a camera picture
        self.video_player.pause()
        time.sleep(1)
        file_name = self.webcam_handler.get_and_store_shot(game_instance = self.session_id, 
            game_name = self.list_selected_games[self.current_game_index], 
            player_name = self.shooter_data.shooter_by_index(self.current_player_index))

        # picture is good, now show some BANG and process the image
        time.sleep(1)
        self.video_player.resume()

        # now store and process the shot 
        self.result_processor.process_arrow_cam_shot(self.shooter_data.shooter_by_index(self.current_player_index), self.list_selected_games[self.current_game_index], self.current_player_arrow_nr, file_name)

        # count the arrow
        self.current_player_arrow_nr += 1
        return

    #####################################################################################
    #------- Handle an manual update of player scores in the result window
    def on_update_manual_result(self, shooter_name: str, game_name: str, arrow_index: int, new_value: int):
        sg.cprint("{} - TRACE: {}.on_update_manual_result()".format(datetime.now(), self.__class__)) 
        self.result_processor.update_manual_result(shooter_name, game_name, arrow_index, new_value)
        return
        
    #####################################################################################
    #------- Handle a close in the result window
    def on_button_close_result_window(self):
        sg.cprint("{} - TRACE: {}.on_button_close_result_window()".format(datetime.now(), self.__class__)) 
        self.result_processor.close_result_window()
        self.result_processor.clear_results()
        return

    #####################################################################################
    #------- Close and clean up
    def close(self):
        sg.cprint("{} - TRACE: {}.close()".format(datetime.now(), self.__class__))

        self.main_window.close()
        self.webcam_handler.close()
        self.bang_detector.stop()        
        self.result_processor.clear_results()
        return
