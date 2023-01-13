import PySimpleGUI as sg
import pygame
import pygame.camera
import pygame.image
from datetime import datetime
import os

from game_modules.app_configuration import AppConfig

## DOCU HERE: https://www.pygame.org/docs/ref/camera.html

class CameraControl:
    
    #######################################################################################
    def __init__(self):
        sg.cprint("{} - TRACE: Initializing class {}.".format(datetime.now(), self.__class__))

        # Load user setting from config file
        self.current_camera = None
        self.current_camera_index = AppConfig.get_user_setting_camera_index()
        self.output_format = AppConfig.CFG_DEFAULT_CAMERA_OUTPUT_FORMAT
        self.last_game_path = ""
        self.last_image_last_game = ""

        ## Configuration Window
        self.config_window = None
        self.config_layout = None

        ## DEFAULT RESOLUTION - FULL HD
        self.image_size_fullhd = AppConfig.CFG_DEFAULT_CAMERA_RESOLUTION
        self.color_space = AppConfig.CFG_DEFAULT_CAMERA_COLOR_SPACE

        # Setup output folder
        self.cam_base_storage_folder = AppConfig.CFG_CAM_PICTURE_STORAGE_PATH
        if os.path.exists(self.cam_base_storage_folder) is False:
                os.mkdir(self.cam_base_storage_folder)

        sg.cprint("{} - Storage location for camera pictures is set to {}.".format(datetime.now(), self.cam_base_storage_folder))

        # init pygame module
        pygame.init()
        pygame.camera.init()
        
        # set default camera
        cam = pygame.camera.Camera(pygame.camera.list_cameras()[self.current_camera_index], self.image_size_fullhd, self.color_space)
        self.update_cam_selection(cam)
        return

    ##############################################################################################################
    def update_cam_selection(self, new_cam):
        sg.cprint("{} - TRACE: {}.update_cam_selection()".format(datetime.now(), self.__class__))

        if self.current_camera is not None:
            self.current_camera.stop()
            self.current_camera = None

        self.current_camera = new_cam
        self.current_camera.start()

        # Store user setting to config file
        AppConfig.set_user_setting_camera_index(self.current_camera_index)
        
        return

    ##############################################################################################################
    def get_last_game_path(self) -> str:
        sg.cprint("{} - TRACE: {}.get_last_game_path()".format(datetime.now(), self.__class__))

        return self.last_game_path

    ##############################################################################################################
    def get_last_image_path(self) -> str:
        sg.cprint("{} - TRACE: {}.get_last_image_path()".format(datetime.now(), self.__class__))

        return self.last_image_last_game

    ##############################################################################################################
    ## Opens a user dialog to select the correct camera
    def configure(self) -> sg.Window:
        sg.cprint("{} - TRACE: {}.configure()".format(datetime.now(), self.__class__))

        # get device full information list
        camera_list = pygame.camera.list_cameras()
        
        self.config_layout = [
            [sg.Text('Verfügbare Kameras:')],
            [sg.Combo(values = camera_list, default_value = camera_list[self.current_camera_index], key = "-CAMERA_INPUT_DEVICE_INDEX-", expand_x = True)],
            [sg.VPush()],
            [sg.Button("Kamera OK", size = (30, 1), pad = (1, 1), expand_x = True)],
        ]

        self.config_window = sg.Window('HSG Bogen Kino - Kamera Einstellungen', 
            self.config_layout, 
            element_justification = 'left', 
            finalize = True, 
            resizable = False,
            size = (400, 150),
            modal = True,
            disable_close = True,
            disable_minimize = True
        )

        return

    ##############################################################################################################
    def close_config_win(self):
        sg.cprint("{} - TRACE: {}.close_config_win()".format(datetime.now(), self.__class__))

        self.config_window.read(timeout = 1, timeout_key = "__TIMEOUT__") 

        cam_name = self.config_window["-CAMERA_INPUT_DEVICE_INDEX-"].get()
        self.current_camera_index = pygame.camera.list_cameras().index(cam_name) 

        cam = pygame.camera.Camera(cam_name, self.image_size_fullhd, self.color_space)
        self.update_cam_selection(cam)

        self.config_window.close()
        self.config_window = None
        return
        
    #######################################################################################
    def close(self):
        sg.cprint("{} - TRACE: {}.close()".format(datetime.now(), self.__class__))

        if self.current_camera is not None:
            self.current_camera.stop()
            self.current_camera = None
    
    #######################################################################################
    def get_and_store_shot(self, game_instance: str, game_name: str, player_name: str) -> str:
        sg.cprint("{} - TRACE: {}.get_and_store_shot()".format(datetime.now(), self.__class__))

        # reading the input using the camera
        image = self.current_camera.get_image()
        
        # saving image in local storage
        ct = datetime.now()
        dir_name = "{}/{}".format(self.cam_base_storage_folder, game_instance)
        self.last_game_path = dir_name
        
        if os.path.exists(dir_name) is False:
            os.mkdir(dir_name)

        file_name = "{:02d}-{:02d}-{:02d}_{}_{}.{}".format(ct.hour, ct.minute, ct.second, game_name, player_name, self.output_format)
        target_file = "{}/{}".format(dir_name, file_name)
        sg.cprint("{} - Saving new camera picture: {}".format(datetime.now(), target_file))
        pygame.image.save(image, target_file)
        self.last_image_last_game = target_file        

        return file_name