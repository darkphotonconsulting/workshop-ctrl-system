import os, sys
import json
#sys.path.append(base_dir)



class RelayInfo(object):
    foo = 'bar'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = "/".join(current_dir.split('/')[0:-1])

    def __init__(self, file_name: str = 'relays.json') -> None:
        #super().__init__()
        data_file = os.path.join(self.__class__.base_dir, 'data', file_name)
        if os.path.exists(data_file):
            with open(data_file, 'r') as file:
                self.user_configured = True
                self.data = json.load(file)
        else:
            print("warning, this object was initialized with empty data, please create ./data/relays.json if you would like that to not happen")
            self.user_configured = False
            self.data = {}
