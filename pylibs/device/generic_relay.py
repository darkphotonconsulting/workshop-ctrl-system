import os, sys
import json
#sys.path.append(base_dir)



class RelayInfo(object):
    """RelayInfo Load in user defined data about a multi-channel relay board.

    One primary function of the headunit system is to intelligently control a multi-channel relay.
    More specifically a ic board with multiple AC/DC relays controllable by IO ports on board, 
    these MUST BE isolated by optocouplers on each channel

    \U000026A0 In order to incorporate relay data, you must define it. 

    \U000026A0 Currently, this class looks for a relays.json file in the './data' directory

    TODO: relay info comes from UI, the class should then query a mongodb to provide relay info
    TODO: also gracefully bail out if there IS no relay info yet

    \U0001F4D3 Generally, the step of adding a relays.json will be replaced by user run steps in a UI interface, 
    and this class may be additional or intermediary until that is so

    The format of the relays.json file is a list of dicts, the following keys are required for each channel

        [
            {
                "model": "SRD-05VDC-SL-C",
                "state": true,
                "description": "relay channel 1 test-pump",
                "manufacturer": "Songle",
                "relay_channel": 1,
                "normally_open": true,
                "ac_voltage_max": 250,
                "ac_voltage_min": 125,
                "dc_voltage_min": 28,
                "dc_voltage_max": 30,
                "ac_amperage_max": 10,
                "ac_amperage_min": 10,
                "dc_amperage_max": 10,
                "dc_amperage_min": 10,
                "activation_type": "direct",
                "activation_voltage": 5
            },
        ...
        ]    
    Attributes:
        data (dict): the relays.json data loaded as a dict
    """
    foo = 'bar'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = "/".join(current_dir.split('/')[0:-2])
    #print(base_dir)
    def __init__(self,
        file_name: str = 'relays.json'
    ) -> None:
        """__init__ Create an object of RelayInfo class

        Pretty simple object that is read in from a user defined file

        If the file does not exist the data object will be empty, create the file and retry

        Args:
            file_name (str, optional): the file name to load, it is expected this is in the './data' directory. Defaults to 'relays.json'.
        """
        data_file = os.path.join(self.__class__.base_dir, 'data', file_name)
        if os.path.exists(data_file):
            with open(data_file, 'r') as file:
                self.user_configured = True
                self.data = json.load(file)
        else:
            print("warning, this object was initialized with empty data, please create ./data/relays.json if you would like that to not happen")
            self.user_configured = False
            self.data = {}
