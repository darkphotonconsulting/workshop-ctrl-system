from os.path import (
    dirname,
    abspath
)

from os import (
    environ,
    urandom
)
from time import (
    sleep
)

from datetime import (
    datetime
)

#import sys
from json import (
    loads,
    dumps
)
from sys import (
    stdout,
    stderr,
    path,
    modules,
    exit
)


from psutil import (
    cpu_times,
    cpu_stats,
    virtual_memory,
    swap_memory,
    sensors_temperatures,
    disk_usage,
    disk_partitions,
    net_io_counters,
)

from typing import (
    Union,
    Any,
    Optional
)

from abc import (
    ABCMeta
)

from threading import (
    Thread,
    ThreadError
)

from signal import (
    alarm,
    signal,
    siginterrupt,
    sigwait
)
from signal import (
    SIGINT,
    SIGUSR1
)
current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
path.append(libs)

from pylibs.mq.rabbit import (
    Rabbit, 
    RabbitAdmin
)


class Metrics(object, metaclass=ABCMeta):
    METRIC_INTERVAL = 60

    @classmethod 
    def __signal_handler(cls,
        signum: int = None,
        frame: Any = None,
    ):
        print(f"received {signum} in {frame}")
        exit(0)

        
        
    def __init__(self,
        interval: Union[int, float] = None
    ) -> None:
        # configure signal handlers
        signal(SIGINT, self.__class__.__signal_handler)
        signal(SIGUSR1, self.__class__.__signal_handler)
        
        self.interval = self.__class__.METRIC_INTERVAL if interval is None else interval
        self.threads = []

    @classmethod
    def __sanitize_message(cls,
        message: Any = None
    ) -> str:
        if isinstance(message, str):
            return message
        elif isinstance(message, (dict, list)):
            return dumps(message, indent=2)
        elif isinstance(message, (int, float)):
            return str(message)
        


    def stream_metric(self, 
        function_name: str = None,
        backend: Any = None,
    ): 
        if function_name == '__init__': return False
        backend = print if backend is None else backend
        try:
            while True:
                backend(getattr(self, function_name)())
                sleep(self.interval)
        except KeyboardInterrupt as interrupt:
            print(f"aborted by user")
            return True

        
class SystemMetrics(Metrics):

    def __init__(self,
        interval: Union[int, float] = None,
    ) -> None:
        super().__init__(interval=interval)


            
    def cputime(self,
    ) -> list:
        timestamp = datetime.now().timestamp()
        data = [
            dict(
                **cpu_times()._asdict(),
                cpuid=i+1, 
                timestamp=timestamp
            ) for i, cpu in enumerate(cpu_times(percpu=True))
        ]
        
        return data

    def cpustats(self,
    ) -> dict:
        timestamp = datetime.now().timestamp()
        data = dict(
                **cpu_stats()._asdict(),
                timestamp=timestamp
        )
        return data



    def vmem(self,
    ) -> dict:
        timestamp = datetime.now().timestamp()
        data = dict(
                **virtual_memory()._asdict(),
                timestamp=timestamp
        )
        as_bytes = [
            'total', 
            'available', 
            'used', 
            'free', 
            'active', 
            'inactive', 
            'buffers', 
            'cached', 
            'shared', 
            'slab', 
            
        ]
        for k,v in data.items():
            if k in as_bytes:
                data[k] = v / 1e3
        # need to convert these values from bytes to 
        return data

        
    def swap(self,
    ) -> dict:
        timestamp = datetime.now().timestamp()
        data = dict(
                **swap_memory()._asdict(),
                timestamp=timestamp
        )
        return data


    def temperatures(self,
    )-> list:
        timestamp = datetime.now().timestamp()
        temps = []
        for key, value in sensors_temperatures().items():
            print(f"on {key}")
            if isinstance(value, list) and len(value)>0:
                for item in value:
                    temps.append(
                        dict(
                            **item._asdict(),
                            timestamp=timestamp
                        )
                    )
        return temps


    def diskusage(self,
    )-> list:
        timestamp = datetime.now().timestamp() 
        usages = []
        disks = [
            dict(
                disk._asdict()
            ) for disk in disk_partitions(all=False)
        ]
        for disk in disks:
            usages.append(
                dict(
                    **disk_usage(disk['mountpoint'])._asdict(),
                    mountpoint=disk['mountpoint'],
                    timestamp=timestamp
                )
            )
        return usages

    def netio(self,
    ) -> list:
        timestamp = datetime.now().timestamp() 
        usages = [
            dict(
                **usage._asdict(),
                nic=nic,
                timestamp=timestamp
            ) for nic, usage in net_io_counters(pernic=True).items()
        ]
        return usages

    def load_threads(self,
        metric_functions: list = None
    ) -> Union[list, bool]:
        metric_functions = ['netio', 'diskusage'] if metric_functions is None else metric_functions
        if len(self.threads)==0:
            for function in metric_functions:
                print(function)
                func = getattr(self, function)        
                self.threads.append(
                    Thread(
                        target=func,
                        
                    )
                )
            return self.threads
        else: return False

    def start_threads(self,
    ) -> list:
        if len(self.threads>0):
            for thread in self.threads:
                thread.start()
        