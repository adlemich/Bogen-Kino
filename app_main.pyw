"""
--> You will need to pip install the modules in requirements.txt

################################################################################################
# PySimpleGui Docu: https://www.pysimplegui.org/en/latest/call%20reference/ 
################################################################################################

"""
import PySimpleGUI as sg
import traceback
from game_modules.app_configuration import AppConfig
from game_engine.game_engine import GameEngine
from game_modules.result_processor import ResultProcessor
from datetime import datetime

################################################################################
## Let the user pick a color theme
def run_theme_chooser(current_theme: str):

    theme_list = ['Default', 'BlueMono', 'BluePurple', 'BrightColors', 'BrownBlue', 'DarkAmber', 'DarkBlack', 'DarkBlue', 'DarkBrown', 'DarkGreen', 'DarkGrey', 
        'DarkPurple', 'DarkRed', 'DarkTanBlue', 'DarkTeal', 'GreenMono', 'GreenTan', 'HotDogStand', 'Kayak', 'LightBlue', 'LightBrown', 
        'LightGreen', 'LightGrey', 'LightPurple', 'LightTeal', 'LightYellow', 'NeutralBlue', 'Python', 'Reddit', 'Reds', 'SandyBeach',  
        'TanBlue', 'TealMono', 'Topanga']

    theme_layout = [
          [sg.Text('Bitte wähle eine Farb-Einstellung.')],
          [sg.Listbox(values = theme_list, default_values = current_theme, expand_x = True, expand_y = True, key='-LIST-THEME-CHOOSER-', enable_events = True, select_mode = sg.LISTBOX_SELECT_MODE_SINGLE)],
          [sg.Button('Farbe OK', expand_x = True)]]

    theme_window = sg.Window(
        'Farb-Einstellungen', 
        theme_layout,
        finalize = True, 
        resizable = False,
        size = (300, 400),
        modal = False,
        disable_close = True,
        disable_minimize = True,
        grab_anywhere = False
    )

    return theme_window

################################################################################
## display App Infos
def display_app_info():

    sg.popup("Bogen Kino Version {}".format(AppConfig.CFG_VERSION), 
                "This application was created and published under open source MIT license and is free to use under these license terms. Please contribute on GitHub with code or by reporting issues and feature ideas: https://github.com/adlemich/Bogen-Kino",
                "With grateful usage of the following open source Python libraries: PySimpleGUI, python-vlc, numpy, pyaudio, opencv-python, pygame ",
                " ",
                "(c) Michael Adler, 2022-2023",
                title = "App-Info", 
                keep_on_top = True, 
                font = ('Arial', 10, 'normal'),
                icon = AppConfig.CFG_HSG_LOGO_ICO_FILE, 
                any_key_closes = True)
    return

################################################################################
## create an invisible window with multiline for debugging information
def setup_debug_window() -> sg.Window:
    win_layout = [
            [sg.Text('Detailed debug information: ')],
            [sg.Multiline("", autoscroll = True, horizontal_scroll = True, auto_refresh = True, echo_stdout_stderr = True, reroute_cprint = True, expand_x = True, expand_y = True, key = '-DEBUG_INFO_OUT-')],
            [sg.Button('Ausblenden')]
        ]

    debug_window = sg.Window('HSG Bogen Kino - Debug Information', 
            win_layout, 
            element_justification = 'left', 
            finalize = True, 
            resizable = True,
            size = (900, 600),
            modal = False,
            disable_close = True,
            disable_minimize = True,
            grab_anywhere = True
        )

    debug_window.hide()

    return debug_window

################################################################################
#------------ The Event Loop ------------#
def main():

    # Load user configuration
    AppConfig.load_user_config()

    # Set global Theme
    sg.theme(AppConfig.get_user_setting_theme())
    # Global sg settings
    sg.set_options(
        icon = AppConfig.CFG_HSG_LOGO_ICO_FILE,
        font = ('Arial', 10, 'normal') 
    )
    theme_window = None

    ## Debug Window
    debug_window = setup_debug_window()
    sg.cprint_set_output_destination(debug_window, "-DEBUG_INFO_OUT-")
    sg.cprint("{} - Bogen Kino {} is starting up... Welcome!!".format(datetime.now(), AppConfig.CFG_VERSION))

    ## the main game instance
    game = GameEngine()

    try:
        while True:

            # Get all events and current data from all UI elements    
            window, event, values = sg.read_all_windows(timeout = AppConfig.CFG_CYCLE_TIMEOUT_MS, timeout_key = "__TIMEOUT__")    
        
            if event in (sg.WINDOW_CLOSED, "Exit"):
                #check which window TODO
                if window.metadata == "main":
                    sg.cprint("{} - EVENT: [Exit] app exit received. Closing application.".format(datetime.now()))
                    break

            ############################################################################# 
            # THE EVENTS FROM THE TOP MENU
            if event == "App Info":
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                display_app_info()
            
            elif event == "Mikrofon":        
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_menu_setting_micro()

            ## This is an event from the micro configuration window
            elif event == "Mikrofon OK":        
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_micro_ok()  

            elif event == "Kamera":        
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_menu_setting_camera()

            ## This is an event from the camera configuration window
            elif event == "Kamera OK":    
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))    
                game.on_button_camera_ok()     

            elif event == "Farben":        
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                theme_window = run_theme_chooser(AppConfig.get_user_setting_theme())

            elif event == "-LIST-THEME-CHOOSER-":        
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                sg.theme(values["-LIST-THEME-CHOOSER-"][0])
                theme_window.close()
                theme_window = run_theme_chooser(values["-LIST-THEME-CHOOSER-"][0])

            elif event == "Farbe OK":
                AppConfig.set_user_setting_theme(values["-LIST-THEME-CHOOSER-"][0])
                sg.theme(AppConfig.get_user_setting_theme())
                # Close and restart all
                theme_window.close()
                game.close()
                game = None
                game = GameEngine()

            ############################################################################# 
            # THE EVENTS FROM THE MAIN FORM
            elif event == "Alle": 
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))       
                game.on_button_alle()

            elif event == "Leeren":
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_leeren()
            
            elif event == "->":
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_nachrechts(values)

            elif event == "<-":
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_nachlinks(values)
            
            elif event == '+':
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_mehr()

            elif event == '-':
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_weniger()

            elif event == 'Namen anpassen':
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_namenanpassen()

            elif event == 'Start':
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_start()

            ## This is an event from the shooter configuration window
            elif event == "Spieler OK":
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_namenanpassen_ok()

            ############################################################################# 
            # THE EVENTS FROM THE PLAYER WINDOW:
            elif event == 'Abbrechen':
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_player_abbrechen()
            
            elif event == '-BUTTON-SCHUSS-':
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_bang()

            ############################################################################# 
            # THE EVENTS FROM THE MENU FOR THE DEBUG WINDOW
            elif event == "Einblenden":
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                debug_window.un_hide()
                debug_window.bring_to_front()

            elif event == "Ausblenden":
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                debug_window.send_to_back()
                debug_window.hide()

            ############################################################################# 
            # THE EVENTS FROM THE RESULTS WINDOW
            elif event == "-BUTTON-RESULTS-CLOSE":
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                game.on_button_close_result_window()                
            
            elif ResultProcessor.MANUAL_ENTRY_FIELD_PREFIX in event:
                sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
                shooter_name, game_name, arrow_index = window[event].metadata
                game.on_update_manual_result(shooter_name, game_name, arrow_index, int(values[event]))

            ############################################################################# 
            ## TIMEOUT - THIS WILL DO CONTINOUS WORK LIKE CHECKING FOR BANGS. NO TRACE LOGS HERE!
            elif event == "__TIMEOUT__":
                game.on_event_loop_timeout()

    except Exception as e:
        sg.cprint("{} - ERROR: Exception occured in main event loop. E = {}".format(datetime.now(), e), text_color = "pink")
        sg.cprint("{} -  --> {}".format(datetime.now(), traceback.format_exc()), text_color = "pink")
        debug_window.un_hide()
        debug_window.bring_to_front()
        debug_window.maximize()
        file_out = open("./logs/crash_{}.log".format(game.session_id), 'w')
        file_out.writelines(debug_window["-DEBUG_INFO_OUT-"].get())        
        file_out.close()
        game.on_button_player_abbrechen()
        sg.popup_ok("SORRY!!! Es ist ein unerwarteter Fehler aufgetreten. Überprüft das Debug-Fenster für Details. OK beendet die Anwendung für dieses Mal - ihr hattet hoffentlich dennoch Spaß damit. ;-)")

    ## STOP IT
    game.close()

    ## Close Debug and save session log
    sg.cprint("{} - Bogen Kino {} is shutting down... Have a nice day!!".format(datetime.now(), AppConfig.CFG_VERSION))
    file_out = open(AppConfig.CFG_LAST_SESSION_LOG_FILE, 'w')
    file_out.writelines(debug_window["-DEBUG_INFO_OUT-"].get())        
    file_out.close()
    debug_window.close()

    return
################################################################################

if __name__ == '__main__':
    main()