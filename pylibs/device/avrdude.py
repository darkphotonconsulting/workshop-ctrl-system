import os 
import sys
import re

# access pylibs path
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
sys.path.append(libs)


from pylibs.constants.constants import (
    AVRDUDE_PART_KEYS,
    AVRDUDE_CONF
)

def preprocess_config(
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

def extract_part_memories(
    part: str = None
) -> str:
    """extract_part_memories [summary]

    [extended_summary]

    Args:
        part (str, optional): [description]. Defaults to None.

    Returns:
        str: [description]
    """
    rgx = re.compile(pattern=f"^\s{{4}}memory\s{{1}}\"(?P<type>\w+)\"\n(?P<memoryBlock>(?:\s+\w+\s+=\s+(?:\w|\d|\s|\"|,|)+[;,]\n)+^\s{{4,6}};)", flags=re.MULTILINE)
    return [memory for memory in re.findall(
        pattern=rgx, 
        string=part, 
        #flags=re.MULTILINE
        )
    ]

def extract_memory_attributes(
    memory: tuple = None
) -> dict:
    attributes = {}
    memory_type = memory[0]
    attributes[memory_type] = {}
    for kv_line in memory[1].split("\n"):
        if '=' in kv_line:
            key, value = [i.strip().replace("\t", "").replace(";", "") for i in kv_line.split("=")]
            attributes[memory_type][key] = value
        else: continue

    return attributes
            
    

def extract_parent_parts(
    conf: str = None
) -> list:
    """extract_parent_parts parse parts from AVRdude configuration



    Args:
        conf (str, optional): a clean AVRdude configuration. Defaults to None.

    Returns:
        list: list of defined part strings
    """
    return [parent_child[0] for parent_child in re.findall(r"(?P<part>^part\n(\s{1,4}.*\n)+)", conf, flags=re.MULTILINE)]

def extract_children_parts(
    conf: str = None
) -> list:
    """extract_children_parts parse parts from AVRdude configuration



    Args:
        conf (str, optional): a clean AVRdude configuration. Defaults to None.

    Returns:
        list: list of defined part strings
    """
    return [child_part[0] for child_part in re.findall(r"(?P<part>^part parent .+\n(\s{1,4}.*\n)+)", conf, flags=re.MULTILINE)]

def extract_part_attributes(
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

def post_process_attributes(
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


def process_config(
    avrdude_conf: str = None
) -> dict:
    data = {}
    # add parent parts
    data['parts'] = []
    avrdude_conf = AVRDUDE_CONF if avrdude_conf is None else avrdude_conf
    conf = preprocess_config(avrdude_conf=avrdude_conf)
    parts = extract_parent_parts(conf)
    for part in parts:
        parsed = post_process_attributes( 
            extract_part_attributes(part)
        )
        if 'id' in parsed:
            data['parts'].append(parsed)
        
    return data
        