import PySimpleGUI as sg
from datetime import datetime

class AppConfig:

    ## VERSION
    CFG_VERSION = "v0.3"

    ## PATHS AND FILES
    CFG_USER_SETTINGS_FILE = "user_settings.json"
    CFG_USER_SETTINGS_PATH = "./"
    CFG_HSG_LOGO_IMG_FILE = "./images/hsg_logo_150px.png"
    CFG_HSG_LOGO_ICO_FILE = "./images/hsg_logo.ico"
    CFG_ARCHERY_TARGET_FILE = "./images/archery_target.png"
    CFG_NO_HIT_MISS_IMAGE_FILE = "./pattern_img/no_hit_image.png"
    CFG_LAST_SESSION_LOG_FILE = "./logs/last_session.log"
    CFG_VIDEO_GAMES_PATH = "./videos"
    CFG_CAM_PICTURE_STORAGE_PATH = "./cam_shots"
    CFG_RESULTS_STORAGE_PATH = "./results"
    
    ## TECHNICAL CONSTANTS
    CFG_CYCLE_TIMEOUT_MS = 50  

    # Defaults for gameplay
    CFG_MAX_PLAYERS       = 12
    CFG_ARROWS_PER_PLAYER = 3
    CFG_POINTS_YELLOW     = 5
    CFG_POINTS_RED        = 3
    CFG_POINTS_WHITE      = 1
    CFG_POINTS_MISS       = 0

    ## DEFAULTS FOR CAMERA
    CFG_DEFAULT_CAMERA_RESOLUTION = (1920, 1080)
    CFG_DEFAULT_CAMERA_OUTPUT_FORMAT = "png"
    CFG_DEFAULT_CAMERA_COLOR_SPACE = "RGB"

    # USER SETTING: THEME
    _CFG_DEFAULT_THEME = 'Topanga'
    _KEY_USER_THEME = "UserTheme"
    _user_setting_theme = _CFG_DEFAULT_THEME

     # USER SETTING: CAMERA_INDEX
    _CFG_DEFAULT_CAMERA_INDEX = 0
    _KEY_USER_CAMERA_INDEX = "UserCamera"
    _user_setting_camera_index = _CFG_DEFAULT_CAMERA_INDEX

    # USER SETTING: MICRO_INDEX
    _CFG_DEFAULT_MICRO_INDEX = 1
    _KEY_USER_MICRO_INDEX = "UserMicrophone"
    _user_setting_micro_index = _CFG_DEFAULT_MICRO_INDEX

    ################################################################################################
    ## Load user settings from file
    @staticmethod
    def load_user_config():
        print("{} - DEBUG: Loading user configuration from file [{}/{}]...".format(datetime.now(), AppConfig.CFG_USER_SETTINGS_PATH, AppConfig.CFG_USER_SETTINGS_FILE))
        
        sg.user_settings_filename(AppConfig.CFG_USER_SETTINGS_FILE, AppConfig.CFG_USER_SETTINGS_PATH)
        sg.user_settings_load()
        
        if sg.user_settings_file_exists(AppConfig.CFG_USER_SETTINGS_FILE, AppConfig.CFG_USER_SETTINGS_PATH):
            # Theme
            AppConfig._user_setting_theme = sg.user_settings_get_entry(AppConfig._KEY_USER_THEME, AppConfig._CFG_DEFAULT_THEME)
            print("{} - DEBUG: | - Loaded key [{}] with value [{}]...".format(datetime.now(), AppConfig._KEY_USER_THEME, AppConfig._user_setting_theme))
            # Camera
            AppConfig._user_setting_camera_index = sg.user_settings_get_entry(AppConfig._KEY_USER_CAMERA_INDEX, AppConfig._CFG_DEFAULT_CAMERA_INDEX)
            print("{} - DEBUG: | - Loaded key [{}] with value [{}]...".format(datetime.now(), AppConfig._KEY_USER_CAMERA_INDEX, AppConfig._user_setting_camera_index))
            # Microphone
            AppConfig._user_setting_micro_index = sg.user_settings_get_entry(AppConfig._KEY_USER_MICRO_INDEX, AppConfig._CFG_DEFAULT_MICRO_INDEX)
            print("{} - DEBUG: | - Loaded key [{}] with value [{}]...".format(datetime.now(), AppConfig._KEY_USER_MICRO_INDEX, AppConfig._user_setting_micro_index))

        return

    ################################################################################################
    @staticmethod
    def set_user_setting_theme(new_theme_value: str):
        sg.cprint("{} - DEBUG: Now storing user setting with key {} with value{}...".format(datetime.now(), AppConfig._KEY_USER_THEME, new_theme_value))
        AppConfig._user_setting_theme = new_theme_value
        sg.user_settings_set_entry(AppConfig._KEY_USER_THEME, AppConfig._user_setting_theme)
        sg.user_settings_save()
        return

    ################################################################################################
    @staticmethod
    def get_user_setting_theme() -> str:
        return AppConfig._user_setting_theme

    ################################################################################################
    @staticmethod
    def set_user_setting_camera_index(new_camera_index_value: str):
        sg.cprint("{} - DEBUG: Now storing user setting with key {} with value{}...".format(datetime.now(), AppConfig._KEY_USER_CAMERA_INDEX, new_camera_index_value))
        AppConfig._user_setting_camera_index = new_camera_index_value
        sg.user_settings_set_entry(AppConfig._KEY_USER_CAMERA_INDEX, AppConfig._user_setting_camera_index)
        sg.user_settings_save()
        return

    ################################################################################################
    @staticmethod
    def get_user_setting_camera_index() -> str:
        return AppConfig._user_setting_camera_index

    ################################################################################################
    @staticmethod
    def set_user_setting_micro_index(new_micro_index_value: str):
        sg.cprint("{} - DEBUG: Now storing user setting with key {} with value{}...".format(datetime.now(), AppConfig._KEY_USER_MICRO_INDEX, new_micro_index_value))
        AppConfig._user_setting_micro_index = new_micro_index_value
        sg.user_settings_set_entry(AppConfig._KEY_USER_MICRO_INDEX, AppConfig._user_setting_micro_index)
        sg.user_settings_save()
        return

    ################################################################################################
    @staticmethod
    def get_user_setting_micro_index() -> str:
        return AppConfig._user_setting_micro_index
