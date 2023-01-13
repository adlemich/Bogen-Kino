import PySimpleGUI as sg
import pyaudio
import struct
import math
from datetime import datetime

from game_modules.app_configuration import AppConfig

##############################################################################################################
##############################################################################################################
class BangDetector(object):
    
    ## CONSTANTS AND DEFAULTS
    INITIAL_TAP_THRESHOLD = 0.025
    FORMAT = pyaudio.paInt16 
    SHORT_NORMALIZE = (1.0/32768.0)
    INPUT_BLOCK_TIME = 0.035
    OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME                    
    UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME 
    MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME

    ##############################################################################################################
    def __init__(self):        
        sg.cprint("{} - TRACE: Initializing class {}.".format(datetime.now(), self.__class__))

        self.current_audio_device_index = AppConfig.get_user_setting_micro_index()
        self.pa = pyaudio.PyAudio()
        self.tap_threshold = self.INITIAL_TAP_THRESHOLD
        self.noisycount = self.MAX_TAP_BLOCKS + 1 
        self.quietcount = 0 
        self.errorcount = 0
        self.input_frames_per_block = 0
        self.stream = None

        self.config_window = None
        self.config_layout = None   

        self.update_device_index()

    ##############################################################################################################
    def get_rms(self, block ):
        #sg.cprint("{} - TRACE: {}.get_rms()".format(datetime.now(), self.__class__)) ## no tracing here, too noisy

        count = len(block)/2
        format = "%dh"%(count)
        shorts = struct.unpack( format, block )
        sum_squares = 0.0
        for sample in shorts:
            n = sample * self.SHORT_NORMALIZE
            sum_squares += n*n

        return math.sqrt( sum_squares / count )
    ##############################################################################################################
    def stop(self):        
        sg.cprint("{} - TRACE: {}.stop()".format(datetime.now(), self.__class__))

        if self.stream is not None:
            if self.stream.is_active():
                self.stream.close()

        self.pa.terminate()

    ##############################################################################################################
    def get_input_device_list(self):
        sg.cprint("{} - TRACE: {}.get_input_device_list()".format(datetime.now(), self.__class__))

        list_r_devices = []

        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            
            in_channels = devinfo["maxInputChannels"]
            in_host_api = devinfo["hostApi"]
            if (in_channels > 0 and in_host_api == 0):
                    sg.cprint("{} - Found a sound input device at index {}: {}".format(datetime.now(), i, devinfo))
                    list_r_devices.append(devinfo)

        return list_r_devices

    ##############################################################################################################
    def update_device_index(self):
        sg.cprint("{} - TRACE: {}.update_device_index()".format(datetime.now(), self.__class__))        

        if (self.stream is not None) and (self.stream.is_active() is True):
            self.stream.close()

        # get full device configuration
        device_info = self.get_input_device_list()

        self.input_frames_per_block = int(device_info[self.current_audio_device_index]["defaultSampleRate"] * self.INPUT_BLOCK_TIME)

        self.stream = self.pa.open(format = self.FORMAT,
            channels = int(device_info[self.current_audio_device_index]["maxInputChannels"]),
            rate = int(device_info[self.current_audio_device_index]["defaultSampleRate"]),
            input = True,
            input_device_index = self.current_audio_device_index,
            frames_per_buffer = self.input_frames_per_block)

    ##############################################################################################################
    ## Returns true if a clap/bang was detected
    def listen(self) -> bool:
        #sg.cprint("{} - TRACE: {}.listen()".format(datetime.now(), self.__class__)) ## no tracing here, too noisy
        
        clap_detected = False

        if (self.stream is not None) and (self.stream.is_active() is True):
            try:
                block = self.stream.read(self.input_frames_per_block)
            except IOError as e:
                self.errorcount += 1
                print( "AUDIO ERRORO - (%d) Error recording: %s"%(self.errorcount,e) )
                self.noisycount = 1
                return False

            amplitude = self.get_rms(block)
            #print("amplitude = {}".format(amplitude))
            if amplitude > self.tap_threshold:
                self.quietcount = 0
                self.noisycount += 1
                if self.noisycount > self.OVERSENSITIVE:
                    self.tap_threshold *= 1.1
            else:            
                if 1 <= self.noisycount <= self.MAX_TAP_BLOCKS:
                    clap_detected = True
                    
                self.noisycount = 0
                self.quietcount += 1
                if self.quietcount > self.UNDERSENSITIVE:
                    self.tap_threshold *= 2
        
        return clap_detected

    ##############################################################################################################
    ## Opens a user dialog to select the correct microphone
    def configure(self) -> sg.Window:
        sg.cprint("{} - TRACE: {}.configure()".format(datetime.now(), self.__class__))
        
        # get device full information list
        device_list = self.get_input_device_list()
        name_list = []
        for dev_info in device_list:
            name_list.append("{}: {}".format(dev_info["index"], dev_info["name"]))
        
        self.config_layout = [
            [sg.Text('Verfügbare Audiogeräte:')],
            [sg.Combo(values = name_list, default_value = name_list[self.current_audio_device_index], key = "-AUDIO_INPUT_DEVICE_INDEX-", expand_x = True)],
            [sg.VPush()],
            [sg.Button("Mikrofon OK", size = (30, 1), pad = (1, 1), expand_x = True)],
        ]

        self.config_window = sg.Window('HSG Bogen Kino - Mikrofon Einstellungen', 
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

        device_entry = self.config_window["-AUDIO_INPUT_DEVICE_INDEX-"].get()
        self.current_audio_device_index = int(device_entry[0:1])
        self.update_device_index()

        # Store user setting to disk
        AppConfig.set_user_setting_micro_index(self.current_audio_device_index)

        self.config_window.close()
        self.config_window = None
        return
