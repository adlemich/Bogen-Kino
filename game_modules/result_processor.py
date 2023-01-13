import cv2 as cv
import os
from datetime import datetime
import PySimpleGUI as sg

from game_modules.app_configuration import AppConfig

###################################################################################################################
###################################################################################################################
###################################################################################################################
class ArrowResult:
    def __init__(self):
        self.cam_image = ""
        self.crop_image = AppConfig.CFG_NO_HIT_MISS_IMAGE_FILE
        self.auto_points = 0
        self.manual_points = 0
        self.final_points = 0
        return

    def to_str(self) -> str:  
        text =  "         |> Camera image        = [{}]\n".format(self.cam_image)
        text += "         |> Crop image          = [{}]\n".format(self.crop_image)
        text += "         |> Automatic points    = [{}]\n".format(self.auto_points)
        text += "         |> Manually set points = [{}]\n".format(self.manual_points)
        text += "         |> Final points        = [{}]\n".format(self.final_points)
        return text

###################################################################################################################
###################################################################################################################
###################################################################################################################
class GameResult:
    def __init__(self):
        self.game_name = ""
        self.game_total_points = 0
        self.arrow_results = [] # an index based array
        return

    def to_str(self) -> str:    
        text =  "   #> Game name = [{}]\n".format(self.game_name)
        text += "      |> Game total points = [{}]\n".format(self.game_total_points)
        arrow = 1
        for a in self.arrow_results:
            text += "      #> Arrow {}:\n".format(arrow)
            text += a.to_str()
            arrow += 1
        return text

###################################################################################################################
###################################################################################################################
###################################################################################################################
class ShooterResult:
    def __init__(self):
        self.shooter_name = ""
        self.shooter_total_points = 0
        self.game_results = {} # a dictonary
        return

    def to_str(self) -> str:   
        text =  " # Shooter: [{}]\n".format(self.shooter_name)
        text += "   |> shooter total points = [{}]\n".format(self.shooter_total_points)
        for k, v in self.game_results.items():
            text += v.to_str()
        return text

###################################################################################################################
###################################################################################################################
###################################################################################################################
class SessionResult:
    def __init__(self):
        self.session_id = ""
        self.cam_image_dir = ""
        self.result_dir = ""
        self.total_arrows = 0
        self.shooter_results = {} # a dictonary
        return
    
    def clear(self):
        self.session_id = ""
        self.cam_image_dir = ""
        self.result_dir = ""
        self.total_arrows = 0
        self.shooter_results.clear()
        return

    def to_str(self) -> str:
        text =  "BOGEN KINO - SESSION RESULTS DATA RECORD\n"
        text += " | Session ID             = [{}]\n".format(self.session_id)
        text += " | Camera image directory = [{}]\n".format(self.cam_image_dir)
        text += " | Result directory       = [{}]\n".format(self.result_dir)
        text += " | Session total arrows   = [{}]\n".format(self.total_arrows)
        for k, v in self.shooter_results.items():
            text += v.to_str()
        return text

###################################################################################################################
###################################################################################################################
###################################################################################################################
class ResultProcessor:

    ## Some constants for field names
    MANUAL_ENTRY_FIELD_PREFIX  = "-INPUT_RESULTS_MANUAL_ARROW"
    ARROW_SCORE_FIELD_TEMPLATE = "-OUTPUT_ARROW_FINAL_SCORE_{}_{}_{}-" #.format(shooter_name, game_name, arrow_index)
    GAME_SUM_FIELD_TEMPLATE    = "-OUTPUT_RESULTS_GAME_POINTS_{}_{}-"  #.format(shooter_name, game_name)
    SHOOTER_SUM_FIELD_TEMPLATE = "-OUTPUT_RESULTS_SHOOTER_POINTS_{}-"  #.format(shooter_name)    
    
    ## default data for the image template matching
    template_img = cv.imread("./pattern_img/target_template.png", cv.IMREAD_COLOR)
    mask_img = cv.imread("./pattern_img/target_mask.png", cv.IMREAD_COLOR)
    match_method = cv.TM_CCORR_NORMED  #match_method = cv.TM_SQDIFF

    ##########################################################################################
    ## 
    def __init__(self):
        sg.cprint("{} - TRACE: Initializing class {}.".format(datetime.now(), self.__class__))

        # The actual session Data
        self.session_results = SessionResult()

        # Init window data
        self.result_window = None

        return

    ##########################################################################################
    """ This is used to init the session results when a session is started
        Requires a list of shooter names and game names, along with the mount of arrows per shooter,  session_id, cam_image_dir and result_dir
    """ 
    def init_session_results(self, list_shooter_names, list_game_names, session_id: str, cam_image_dir: str, result_dir: str):
        sg.cprint("{} - TRACE: {}.init_session_results(list_shooter_names = {}, list_game_names = {}, session_id = {}, cam_image_dir = {}, result_dir = {})".format(datetime.now(), self.__class__, 
            list_shooter_names, list_game_names, session_id, cam_image_dir, result_dir))

        total_arrow_cout = 0

        # Make sure the results dir exists
        if os.path.exists(result_dir) is False:
            os.mkdir(result_dir)

        # Set the base data
        self.session_results.session_id = session_id
        self.session_results.cam_image_dir = cam_image_dir
        self.session_results.result_dir = result_dir

        # Build the inital result set with correct amount of array elements
        for shooter in list_shooter_names:
            # Add a shooter to session results
            self.session_results.shooter_results[shooter] = ShooterResult()
            self.session_results.shooter_results[shooter].shooter_name = shooter

            for game in list_game_names:
                # Add a game to the shooter results
                self.session_results.shooter_results[shooter].game_results[game] = GameResult()
                self.session_results.shooter_results[shooter].game_results[game].game_name = game

                for i in range (0, AppConfig.CFG_ARROWS_PER_PLAYER):
                    # add arrows to the game
                    total_arrow_cout += 1
                    self.session_results.shooter_results[shooter].game_results[game].arrow_results.append(ArrowResult())

        self.session_results.total_arrows = total_arrow_cout
        return

    ##########################################################################################
    """ Reset, clear all session results after a game completed.    
    """ 
    def clear_results(self):
        self.session_results.clear()       
        return

    ##########################################################################################
    """ This function allows to register an image for an arrow result, it will process the image directly
        Parameter arrow_nr must be between 1 and ARROWS_PER_GAME.
    """ 
    def process_arrow_cam_shot(self, shooter_name: str, game_name: str, arrow_nr: int, cam_shot_image_file: str) -> bool:
        sg.cprint("{} - TRACE: {}.process_arrow_cam_shot(shooter_name = {}, game_name = {}, arrow_nr = {}, cam_shot_image_file = {})".format(datetime.now(), self.__class__, 
            shooter_name, game_name, arrow_nr, cam_shot_image_file))

        ## Check input
        if arrow_nr < 1 or arrow_nr > AppConfig.CFG_ARROWS_PER_PLAYER:
            sg.cprint("{} - ERROR: Cannot process camera image for arrow nr {}, must be between 1 and {}.".format(datetime.now(), arrow_nr, AppConfig.CFG_ARROWS_PER_PLAYER))
            return False

        ## Look for the right shooter entry and work on it
        shooter_rec = self.session_results.shooter_results.get(shooter_name, None)
        if (shooter_rec is None):
            # NOT FOUND
            sg.cprint("{} - ERROR: Cannot process camera image for shooter [{}] in game [{}] on arrow with image [{}]. Could not find a matching entry in shooter list!!".format(datetime.now(), shooter_name, game_name, cam_shot_image_file))
            return False

        ## Look for the right game entry and work on it
        game_rec = self.session_results.shooter_results[shooter_name].game_results.get(game_name, None)
        if (game_rec is None):
            # NOT FOUND
            sg.cprint("{} - ERROR: Cannot process camera image for shooter [{}] in game [{}] on arrow with image [{}]. Could not find a matching entry in game list!!".format(datetime.now(), shooter_name, game_name, cam_shot_image_file))
            return False

        # Ok, not is save to directly manipulate
        sg.cprint("{} - DEBUG: Processing camera image for shooter [{}] in game [{}] on arrow with image [{}]... ".format(datetime.now(), shooter_name, game_name, cam_shot_image_file))
        ## Extract the target piece from the original image and store in results folder
        input_image_file = "{}/{}".format(self.session_results.cam_image_dir, cam_shot_image_file)
        output_image_file = "{}/{}".format(self.session_results.result_dir, cam_shot_image_file)

        self.session_results.shooter_results[shooter_name].game_results[game_name].arrow_results[arrow_nr - 1].cam_image = input_image_file
        self.session_results.shooter_results[shooter_name].game_results[game_name].arrow_results[arrow_nr - 1].crop_image = output_image_file

        self.extract_target_from_image(input_image_file, output_image_file)

        return True

    ##########################################################################################
    ##
    def extract_target_from_image(self, source_image_file: str, output_file: str):

        sg.cprint("{} - TRACE: {}.extract_target_from_image(source_image_file = {}, output_file = {})".format(datetime.now(), self.__class__, source_image_file, output_file))
        # Load source file
        source_img = cv.imread(source_image_file, cv.IMREAD_COLOR)

        # Perform match operations.
        
        result = cv.matchTemplate(source_img, self.template_img, self.match_method, mask = self.mask_img) 

        ## [normalize]
        cv.normalize( result, result, 0, 1, cv.NORM_MINMAX, -1 )

        ## [best_match]
        _minVal, _maxVal, minLoc, maxLoc = cv.minMaxLoc(result, None)

         ## [match_loc]
        if (self.match_method == cv.TM_SQDIFF):
            matchLoc = minLoc
        else:
            matchLoc = maxLoc
            
        ## Draw an rectangle to the original image
        cv.rectangle(source_img, matchLoc, (matchLoc[0] + self.template_img.shape[0], matchLoc[1] + self.template_img.shape[1]), (0,0,0), 2, 8, 0 )
        cv.imwrite(source_image_file, source_img)
        
        rows_start = matchLoc[1]
        rows_stop = rows_start + self.template_img.shape[1]
        cols_start = matchLoc[0]
        cols_stop = cols_start + self.template_img.shape[0]
        # [rows, columns]
        cropped_img = source_img[rows_start:rows_stop, cols_start:cols_stop]

        # Write to target file
        cv.imwrite(output_file, cropped_img)

        return

    ##########################################################################################
    ##
    def calculate_results(self):
        sg.cprint("{} - TRACE: {}.calculate_results()".format(datetime.now(), self.__class__))

        arrow_points = 0
        game_points = 0
        shooter_points = 0

        for shooter_i, shooter_name in enumerate(self.session_results.shooter_results):

            for game_i, game_name in enumerate(self.session_results.shooter_results[shooter_name].game_results):

                for arrow_i, arrow_rec in enumerate(self.session_results.shooter_results[shooter_name].game_results[game_name].arrow_results):
                    
                    if arrow_rec.manual_points != arrow_rec.auto_points:
                        arrow_points = arrow_rec.manual_points
                    else:
                        arrow_points = arrow_rec.auto_points

                    # Update arrow final points
                    sg.cprint("{} - DEBUG: Using result for shooter [{}] in game [{}] for arrow # [{}] -> score = [{}]... ".format(datetime.now(), shooter_name, game_name, arrow_i + 1, arrow_points))
                    self.session_results.shooter_results[shooter_name].game_results[game_name].arrow_results[arrow_i].final_points = arrow_points
                    game_points += arrow_points
                    arrow_points = 0

                # Update game
                sg.cprint("{} - DEBUG: Calculated result for shooter [{}] in game [{}] with total game score = [{}]... ".format(datetime.now(), shooter_name, game_name, game_points))
                self.session_results.shooter_results[shooter_name].game_results[game_name].game_total_points = game_points
                shooter_points += game_points
                game_points = 0

            # Update Shooter
            sg.cprint("{} - DEBUG: Calculated result for shooter [{}] total session score = [{}]... ".format(datetime.now(), shooter_name, game_name, shooter_points))
            self.session_results.shooter_results[shooter_name].shooter_total_points = shooter_points
            shooter_points = 0

        return

    ##########################################################################################
    ##
    def show_result_window(self):
        sg.cprint("{} - TRACE: {}.show_result_window()".format(datetime.now(), self.__class__))

        ## First calculate results
        self.calculate_results()

        ## Build the Screen
        sg.cprint("{} - DEBUG: Will now render the result screen for our result set:".format(datetime.now()))
        sg.cprint(self.session_results.to_str())

        result_win_layout = [ 
            [sg.Text("Ergebnisse für die Session {}".format(self.session_results.session_id)), sg.Push(background_color = "yellow")],
            [sg.HorizontalSeparator()],
            [sg.Text("   Spiel", size = (22, 2)), sg.Text("Pfeil 1", size = (31, 2)), sg.Text("Pfeil 2", size = (31, 2)), sg.Text("Pfeil 3", size = (31, 2)), sg.Text("Punkte Spiel", size = (12, 2))]
         ]

        main_column_layout = []
        for shooter_name, shooter_rec in self.session_results.shooter_results.items():
            shooter_frame_layout = []

            for game_name, game_rec in self.session_results.shooter_results[shooter_name].game_results.items():

                allowed_point_values = [AppConfig.CFG_POINTS_YELLOW, AppConfig.CFG_POINTS_RED, AppConfig.CFG_POINTS_WHITE, AppConfig.CFG_POINTS_MISS]
                game_frame_layout_line = [sg.Text(game_name, size = (20, 1))]
                
                for arrow_index in range(0, len(self.session_results.shooter_results[shooter_name].game_results[game_name].arrow_results)):

                    point_frame = [
                        [sg.Text("Auto-P: {}".format(game_rec.arrow_results[arrow_index].auto_points), size = (16, 1), text_color = "gray")],
                        [sg.Text("Man. Punkte:", text_color = "gray"), 
                        sg.Combo(allowed_point_values, game_rec.arrow_results[arrow_index].manual_points, size = (3, 1), enable_events = True, 
                            key = "{}_{}_{}_{}-".format(self.MANUAL_ENTRY_FIELD_PREFIX, arrow_index, shooter_name, game_name), metadata = (shooter_name, game_name, arrow_index))],
                        [sg.Text("Punkte: {}".format(game_rec.arrow_results[arrow_index].final_points), size = (20, 1), key = self.ARROW_SCORE_FIELD_TEMPLATE.format(shooter_name, game_name, arrow_index))]
                    ]
                    game_frame_layout_line.append(sg.Image(source = game_rec.arrow_results[arrow_index].crop_image, subsample = 2))
                    game_frame_layout_line.append(sg.Frame("", layout = point_frame, border_width = 0, vertical_alignment = "top"))

                game_frame_layout_line.append(sg.Text("{}".format(game_rec.game_total_points), auto_size_text = True, size = (12, 1), key = self.GAME_SUM_FIELD_TEMPLATE.format(shooter_name, game_name)))

                game_frame_layout = [game_frame_layout_line]
                shooter_frame_layout.append([sg.Frame("", layout = game_frame_layout, border_width = 0, expand_x = True, vertical_alignment = "top")])

            frame_title = "{}: {} Punkte".format(shooter_name, shooter_rec.shooter_total_points)
            main_column_layout.append([
                sg.Frame(frame_title, title_color = "red", layout = shooter_frame_layout, title_location = sg.TITLE_LOCATION_TOP_LEFT, font = ("Arial", 16, "bold"), border_width = 2, expand_x = True, vertical_alignment = "top", 
                    key = self.SHOOTER_SUM_FIELD_TEMPLATE.format(shooter_name))
            ])    
        
        result_win_layout.append([sg.Column(main_column_layout, scrollable = True, vertical_scroll_only = True, expand_x = True, expand_y = True)])
        result_win_layout.append([sg.HorizontalSeparator()])
        result_win_layout.append([
            sg.Button("Schließen", key = "-BUTTON-RESULTS-CLOSE"), 
            sg.Push(), 
            sg.Text("Punkte-Wertung: "), 
            sg.Text(" GELB: {} Punkte ".format(AppConfig.CFG_POINTS_YELLOW), text_color = "yellow"), 
            sg.Text(" ROT: {} Punkte ".format(AppConfig.CFG_POINTS_RED), text_color = "red"), 
            sg.Text(" WEISS: {} Punkt ".format(AppConfig.CFG_POINTS_WHITE), text_color = "white")
        ])
      
        ## Start Window
        self.result_window = sg.Window('HSG Bogen Kino - Ergebnisse', 
            result_win_layout, 
            element_justification = 'left', 
            finalize = True, 
            resizable = True,
            location = (0, 0),
            size = sg.Window.get_screen_size(),
            no_titlebar = False,
            keep_on_top = False,
            modal = False,
            disable_close = True
        )
        self.result_window.maximize()
        return
        
    ##########################################################################################
    ##
    def close_result_window(self):
        sg.cprint("{} - TRACE: {}.close_result_window()".format(datetime.now(), self.__class__))

        # Save the results into a file
        file_name = "{}/{}.txt".format(self.session_results.result_dir, self.session_results.session_id)
        f = open(file_name, "w")
        f.write(self.session_results.to_str())
        f.close()

        # Close the Window
        if self.result_window is not None:
            self.result_window.close()
            self.result_window = None

        return

    ##########################################################################################
    ##
    def update_manual_result(self, shooter_name: str, game_name: str, arrow_index: int, new_value: int):
        sg.cprint("{} - TRACE: {}.update_manual_result(shooter_name = {}, game_name = {}, arrow_index = {}, new_value = {})".format(datetime.now(), self.__class__, shooter_name, game_name, arrow_index, new_value))

        ## Check arrow index
        if arrow_index < 0 or arrow_index > AppConfig.CFG_ARROWS_PER_PLAYER - 1:
            sg.cprint("{} - ERROR: Cannot update manual result for arrow nr {}, must be between 0 and {}.".format(datetime.now(), arrow_index, AppConfig.CFG_ARROWS_PER_PLAYER - 1))
            return False

        ## Look for the right shooter entry and work on it
        shooter_rec = self.session_results.shooter_results.get(shooter_name, None)
        if (shooter_rec is None):
            # NOT FOUND
            sg.cprint("{} - ERROR: Cannot update manual result for shooter [{}] in game [{}] on arrow with index [{}]. Could not find a matching entry in shooter list!!".format(datetime.now(), shooter_name, game_name, arrow_index))
            return False

        ## Look for the right game entry and work on it
        game_rec = self.session_results.shooter_results[shooter_name].game_results.get(game_name, None)
        if (game_rec is None):
            # NOT FOUND
            sg.cprint("{} - ERROR: Cannot update manual result for shooter [{}] in game [{}] on arrow with index [{}]. Could not find a matching entry in game list!!".format(datetime.now(), shooter_name, game_name, arrow_index))
            return False

        # Ok, not is save to directly manipulate
        sg.cprint("{} - DEBUG: Processing manual update for shooter [{}] in game [{}] on arrow with index [{}]... ".format(datetime.now(), shooter_name, game_name, arrow_index))

        self.session_results.shooter_results[shooter_name].game_results[game_name].arrow_results[arrow_index].manual_points = new_value

        # Recalculate and update the screen
        self.calculate_results()
        self.update_screen_point_sums()

        return

    ##########################################################################################
    ##
    def update_screen_point_sums(self):
        sg.cprint("{} - TRACE: {}.update_screen_point_sums()".format(datetime.now(), self.__class__))
        
        sg.cprint("{} - DEBUG: Will now re-render the result screen for our result set:".format(datetime.now()))
        sg.cprint(self.session_results.to_str())

        for shooter_name, shooter_rec in self.session_results.shooter_results.items():
            text = "{}: {} Punkte".format(shooter_name, shooter_rec.shooter_total_points)
            shooter_score_field_name = self.SHOOTER_SUM_FIELD_TEMPLATE.format(shooter_name)
            self.result_window[shooter_score_field_name].update(value = text)

            for game_name, game_rec in self.session_results.shooter_results[shooter_name].game_results.items():
                game_score_field_name = self.GAME_SUM_FIELD_TEMPLATE.format(shooter_name, game_name)
                self.result_window[game_score_field_name].update(value = game_rec.game_total_points)

                for arrow_i, arrow_rec in enumerate(self.session_results.shooter_results[shooter_name].game_results[game_name].arrow_results):
                    text = "Punkte: {}".format(arrow_rec.final_points)
                    arrow_score_field_name = self.ARROW_SCORE_FIELD_TEMPLATE.format(shooter_name, game_name, arrow_i) 
                    self.result_window[arrow_score_field_name].update(value = text)

        self.result_window.refresh()
        return


#############################################################################################################################
"""
if __name__ == "__main__":
    
    ct = datetime.now()
    session_id = "BogenKino-{:04d}-{:02d}-{:02d}_{:02d}-{:02d}".format(ct.year, ct.month, ct.day, ct.hour, ct.minute)

    ip = ResultProcessor()
    ip.init_session_results(["Hawkeye", "Micha", "Sebastian", "Martina"], ["Wiese", "Winterhaus"], session_id, "./cam_shots/2023-01-09_19-54", "./results/2023-01-09_19-54")

    ip.process_arrow_cam_shot("Hawkeye", "Wiese", 1, "19-55-07_Wiese_Hawkeye.png")
    ip.process_arrow_cam_shot("Hawkeye", "Wiese", 2, "19-55-18_Wiese_Hawkeye.png")
    ip.process_arrow_cam_shot("Hawkeye", "Wiese", 3, "19-55-34_Wiese_Hawkeye.png")

    ip.process_arrow_cam_shot("Hawkeye", "Winterhaus", 1, "19-56-14_Winterhaus_Hawkeye.png")
    ip.process_arrow_cam_shot("Hawkeye", "Winterhaus", 2, "19-56-32_Winterhaus_Hawkeye.png")
    ip.process_arrow_cam_shot("Hawkeye", "Winterhaus", 3, "19-56-49_Winterhaus_Hawkeye.png")

    ip.process_arrow_cam_shot("Micha", "Wiese", 1, "19-55-07_Wiese_Micha.png")
    ip.process_arrow_cam_shot("Micha", "Wiese", 2, "19-55-18_Wiese_Micha.png")
    ip.process_arrow_cam_shot("Micha", "Wiese", 3, "19-55-34_Wiese_Micha.png")

    ip.process_arrow_cam_shot("Micha", "Winterhaus", 1, "19-56-14_Winterhaus_Micha.png")
    ip.process_arrow_cam_shot("Micha", "Winterhaus", 2, "19-56-32_Winterhaus_Micha.png")
    ip.process_arrow_cam_shot("Micha", "Winterhaus", 3, "19-56-49_Winterhaus_Micha.png")

    ip.process_arrow_cam_shot("Sebastian", "Wiese", 1, "19-55-07_Wiese_Micha.png")
    ip.process_arrow_cam_shot("Sebastian", "Wiese", 2, "19-55-18_Wiese_Micha.png")
    ip.process_arrow_cam_shot("Sebastian", "Wiese", 3, "19-55-34_Wiese_Micha.png")

    ip.process_arrow_cam_shot("Sebastian", "Winterhaus", 1, "19-56-14_Winterhaus_Micha.png")
    ip.process_arrow_cam_shot("Sebastian", "Winterhaus", 2, "19-56-32_Winterhaus_Micha.png")
    ip.process_arrow_cam_shot("Sebastian", "Winterhaus", 3, "19-56-49_Winterhaus_Micha.png")

    ip.process_arrow_cam_shot("Martina", "Wiese", 1, "19-55-07_Wiese_Micha.png")
    ip.process_arrow_cam_shot("Martina", "Wiese", 2, "19-55-18_Wiese_Micha.png")
    ip.process_arrow_cam_shot("Martina", "Wiese", 3, "19-55-34_Wiese_Micha.png")

    ip.process_arrow_cam_shot("Martina", "Winterhaus", 1, "19-56-14_Winterhaus_Micha.png")
    ip.process_arrow_cam_shot("Martina", "Winterhaus", 2, "19-56-32_Winterhaus_Micha.png")
    ip.process_arrow_cam_shot("Martina", "Winterhaus", 3, "19-56-49_Winterhaus_Micha.png")

     # Set global Theme
    sg.theme('DarkAmber')
    # Global sg settings
    sg.set_options(
        font = ('Arial', 10, 'normal') 
    )

    ip.show_result_window()

    while True:

        # Get all events and current data from all UI elements    
        window, event, values = sg.read_all_windows(timeout = 100, timeout_key = "__TIMEOUT__")    
    
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        elif event == "-BUTTON-RESULTS-CLOSE":
            sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
            ip.close_result_window()
            break
        elif ResultProcessor.MANUAL_ENTRY_FIELD_PREFIX in event:
            sg.cprint("{} - EVENT: [{}] received.".format(datetime.now(), event))
            shooter_name, game_name, arrow_index = window[event].metadata
            ip.update_manual_result(shooter_name, game_name, arrow_index, int(values[event]))
"""