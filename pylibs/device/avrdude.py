""" avrdude helper module
This module contains helper methods for parsing information from avrdude conf, and possibly AVRdude binary executions to help enhance stability of headunit arduino components
"""
import os 
import sys
import re
from shutil import (
    which
)
import subprocess
from subprocess import (
    run,
    Popen,
    STDOUT,
    PIPE
)
from serial import Serial, SerialException, SerialTimeoutException
from struct import pack
from array import array
from time import sleep

# access pylibs path
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
sys.path.append(libs)


from pylibs.constants.constants import (
    AVRDUDE_PART_KEYS,
    AVRDUDE_CONF,
    AVRDUDE_BIN,
)

def avrconf(
    avrdude_conf: str  = None,
) -> str:
    """preprocess_config pre-processes an AVRdude configuration file

    - removes 
    
        - comment lines

        - empty lines and lines with only new line characters
        
    Args:
    
        avrdude_conf (str, optional): The path to a avrdude configuration file. Defaults to None.

    Returns:
    
        str: a clean avrdude configuration file as a string
    """
    avrdude_conf = AVRDUDE_CONF if avrdude_conf is None else avrdude_conf
    conf = ""
    with open(avrdude_conf, 'r') as file:
        for line in file.readlines():
            # things to ignore
            if line.startswith('#'): # comments
                continue
            if line == "": # blank lines
                continue
            if re.match(
                r"^\n$",
                line        
            ): # lines with only '\n'
                continue

            # things to fix
            if re.match(
                r".+ (?P<comment>\/\* .+ \*\/)",
                line     
            ): # remove C style comments /* */
                line = re.sub(r"\/\* .+ \*\/", "", line)
            # rebuild configuration
            conf = conf + line
    return conf

def parts(
    conf: str = None
) -> list:
    """extract_parent_parts parse parts from AVRdude configuration



    Args:
        conf (str, optional): a clean AVRdude configuration. Defaults to None.

    Returns:
        list: list of defined part strings
    """
    return [parent_child[0] for parent_child in re.findall(r"(?P<part>^part\n(\s{1,4}.*\n)+)", conf, flags=re.MULTILINE|re.VERBOSE)]

def childparts(
    conf: str = None
) -> list:
    """extract_children_parts parse parts from AVRdude configuration



    Args:
        conf (str, optional): a clean AVRdude configuration. Defaults to None.

    Returns:
        list: list of defined part strings
    """
    return [child_part[0] for child_part in re.findall(r"(?P<part>^part parent .+\n(\s{1,4}.*\n)+)", conf, flags=re.MULTILINE)]

def mem(
    part: str = None
) -> list:
    """extract_part_memories [summary]

    [extended_summary]

    Args:
        part (str, optional): [description]. Defaults to None.

    Returns:
        str: [description]
    """
    # ^\s{4}memory\s{1}\"(?P<type>\w+)\"\n(?P<memoryBlock>(?:\s{8}\w+\s+=\s+[\s\w\",]+[;,]+[\n]+)+)^\s{6};
    #rgx = re.compile(pattern=f"^\s{{4}}memory\s{{1}}\"(?P<type>\w+)\"\n(?P<memoryBlock>(?:\s+\w+\s+=\s+(?:\w|\d|\s|\"|,|)+[;,]\n)+^\s{{4,6}};)", flags=re.MULTILINE|re.DEBUG)
    # refactor rgx
    rgx = re.compile(pattern=f"^\s{{4}}memory\s{{1}}\"(?P<type>\w+)\"\n(?P<memoryBlock>(?:\s{{8}}\w+\s+=\s+[\s\w\",]+[;,]+[\n]+)+)^\s{{6}};", flags=re.MULTILINE)
    return [memory for memory in re.findall(
        pattern=rgx, 
        string=part, 
        )
    ]

def progs(
    conf: str = None
) -> list:
    """extract_parent_programmers [summary]

    [extended_summary]

    Args:
        conf (str, optional): [description]. Defaults to None.

    Returns:
        list: [description]
    """
    return [programmer for programmer in re.findall(r"^programmer$\n(?P<programmer>(?:\s{2}\w+\s{1,}=\s{1,}(?:\"|\s|\w)+?[;,]{1,}[\n]{1,}){1,})^;\n", conf, flags=re.MULTILINE|re.VERBOSE)]

def childprogs(
    conf: str = None
) -> list:
    return [programmer for programmer in re.findall(r"""^programmer\s{1}parent\s{1}\"(?P<parent>\w+)\"\n(?P<body>(?:\s|\w|=|\"|;)+^;)""", conf, flags=re.MULTILINE|re.VERBOSE)]

def memattribs(
    memory: tuple = None
) -> dict:
    """extract_memory_attributes [summary]

    [extended_summary]

    Args:
        memory (tuple, optional): [description]. Defaults to None.

    Returns:
        dict: [description]
    """
    attributes = {}
    memory_type = memory[0]
    attributes[memory_type] = {}
    for kv_line in memory[1].split("\n"):
        if '=' in kv_line:
            key, value = [i.strip().replace("\t", "    ").replace(";", "") for i in kv_line.split("=")]
            attributes[memory_type][key] = value
        else: continue

    return attributes



def progattribs(
    programmer: str = None
) -> dict:
    """extract_programmer_attributes [summary]

    [extended_summary]

    Args:
        programmer (str, optional): [description]. Defaults to None.

    Returns:
        dict: [description]
    """
    attributes = {}
    for kv_line in programmer.split("\n"):
        if '=' in kv_line:
            key, value = [i.strip().replace('"', '').replace(';', '') for i in kv_line.split('=')]
            attributes[key] = value
    return attributes
            
def childprogattribs(
    programmer: str = None
) -> dict:
    """childprogattribs [summary]

    [extended_summary]

    Args:
        programmer (str, optional): [description]. Defaults to None.

    Returns:
        dict: [description]
    """
    attributes = {}
    attributes['parent'] = programmer[0]
    for kv_line in programmer[-1].split("\n"):
        if '=' in kv_line:
            key, value = [i.strip().replace('"', '').replace(';', '') for i in kv_line.split('=')]
            attributes[key] = value

    return attributes

def partattribs(
    part: str = None
) -> dict:
    """extract_part_attributes parse a part str into a dictionary

    converts a part definition from text to dict

    Args:
        part (str, optional): A part string. Defaults to None.

    Returns:
        dict: the part represented as a dict
    """
    attributes = {}
    # removes the 'part' header
    part = "\n".join(
        part.split("\n")[1:]
    )  
    rgx = re.compile(
        pattern=f"\s{{1,4}}(?P<key>(?:{'|'.join(AVRDUDE_PART_KEYS)}))\s{{1,}}=[\n\s+]?(?P<value>\s{{1,}}(?:\w|\d|,|\s|\n|\")+);",
        flags=re.MULTILINE
    )
    for item in re.findall(
        rgx, 
        part
    ):
        if len(item) == 0: continue
        attributes[item[0].strip()] = item[1].strip().replace('"', '')
        
    return attributes


def childpartattribs(
    part: str = None
) -> dict:
    """extract_child_part_attributes 

    [extended_summary]

    Args:
        part (str, optional): [description]. Defaults to None.

    Returns:
        dict: [description]
    """
    attributes = {}
    # extract parent from first line 
    parent_line = part.split("\n")[0]
    #print(f"parent line: {parent_line}")
    part_parent = re.match(
        pattern=r"part parent\s{1,}\"(?P<parent_name>.+)\"",
        string=parent_line 
    ).group(1)

    attributes[part_parent] = {}
    
    lines = part.split("\n")[1:]
    
    for line in lines:
        if '=' in line:
            key, value = [i.strip().replace('"', "").replace(";", "") for i in line.split("=")]
            attributes[part_parent][key] = value
    
    return attributes    
    

def postprocessattribs(
    attributes: dict = None
) -> dict:
    """post_process_attributes post-process

    Sets pythonic values for select entries 
    
    Args:
        attributes (dict, optional): a dictionary of attributes. Defaults to None.

    Returns:
        dict: an updated dictionary of attributes
    """
    yesorno = lambda i: True if i == 'yes' else False
    newlines = re.compile(pattern=f".+?\n.+?")
    for k,v in attributes.items():
        if v == 'yes' or v == 'no': # convert yes/no to bools
            attributes[k] = yesorno(v)

        if newlines.match(v): # multi-line str vals cleaned & stored as list
            attributes[k] = [
                i.strip().replace('"', '').replace(',', '') for i in v.split("\n")
            ]

    return attributes


def processconfig(
    avrdude_conf: str = None
) -> dict:
    """process_config [summary]

    [extended_summary]

    Args:
        avrdude_conf (str, optional): [description]. Defaults to None.

    Returns:
        dict: [description]
    """
    data = {}
    # add parent parts
    data['parts'] = {}
    data['programmers'] = {}
    #data['part_children'] = []
    avrdude_conf = AVRDUDE_CONF if avrdude_conf is None else avrdude_conf
    conf = avrconf(avrdude_conf=avrdude_conf)
    avrparts = parts(conf)
    children_parts = childparts(conf)
    programmers = progs(conf)

    
    for programmer in programmers: # populate programmers
        prog = progattribs(programmer)
        data['programmers'][prog['id']] = prog
        
    for part in avrparts: # populate parts
        parsed = postprocessattribs( 
            partattribs(part)
        )
        if 'id' in parsed:
            part_id = parsed['id']
            data['parts'][part_id] = parsed
            
            data['parts'][parsed['id']]['memory'] = {}
            memories = mem(part=part)
            for memory in memories: # add memory data for part
                memory = memattribs(memory)
                memory_type = list(memory.keys())[0]
                data['parts'][parsed['id']]['memory'][memory_type] = memory[memory_type]
    for part in children_parts: # add device children
        parsed = childpartattribs(part)
        #data['part_children'].append(parsed)
        parent_id = list(parsed.keys())[0]
        if parent_id in data['parts']:
            data['parts'][parent_id]['child_device'] = parsed
    return data


def sig(
  device_id: str = None, 
  device_protocol: str = None,
  baudrate: int = None,
  device_node: str = None,
) -> str:
    device_id = "atmega2560" if device_id is None else device_id 
    device_protocol = "wiring" if device_protocol is None else device_protocol
    baudrate = 115200 if baudrate is None else baudrate
    device_node = "/dev/ttyACM0" if device_node is None else device_node
    print('executing: ',' '.join([
        AVRDUDE_BIN, 
        '-q', 
        '-V', 
        '-p', device_id, 
        '-C', AVRDUDE_CONF, 
        '-D', 
        '-c', device_protocol, 
        '-b', str(baudrate), 
        '-P', device_node, 
        '-U', 'signature:r:/dev/stdout:i' 
        ]))
    command = run(
        [
            AVRDUDE_BIN, 
            '-q', 
            '-V', 
            '-p', device_id, 
            '-C', AVRDUDE_CONF, 
            '-D', 
            '-c', device_protocol, 
            '-b', str(baudrate), 
            '-P', device_node, 
            '-U', 'signature:r:/dev/stdout:i' 
        ],
        capture_output=True,
    )
    if command.returncode==0:
        signature = command.stdout.decode(encoding='UTF-8').split("\n")[0][9:-2]
        return signature
    else:
        return command.stderr

def validatesig(
    device_id: str = None,
    device_node: str = None,
    device_protocol: str = None,
    baudrate: int = None,
    data: dict = None
) -> bool:
    # setup
    device_id = "m2560" if device_id is None else device_id
    device_node = "/dev/ttyACM0" if device_node is None else device_node
    device_protocol = "wiring" if device_protocol is None else device_protocol
    baudrate = 115200 if baudrate is None else baudrate
    data = processconfig(avrdude_conf=AVRDUDE_CONF) if data is None else data
    device_data = data.get('parts', None).get(device_id, None)
    signature = sig(device_id=device_id)
    print(f"got device signature: {signature}")
    if device_data is not None:
        s = device_data.get('signature', None)
        print(f"data: {s}")
        if s is not None:
            expected_signature = "".join(
                [i[2:] for i in s.split(' ')]
            ).upper()
            print(f"expected signature: {expected_signature}")
            return signature == expected_signature
        else: return False
    else: return False