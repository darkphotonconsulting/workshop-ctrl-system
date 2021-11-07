from os.path import (
    exists,
    dirname,
    abspath,
    join,
)

from io import BytesIO

from os import (
    environ,
    urandom
)

from time import (
    sleep
)

from json import (
    load,
    loads,
    dump,
    dumps,
)
from sys import (
    stdout,
    stderr,
    path,
    modules
)
from time import sleep
from typing import (
    Union,
    Any,
    Optional,
    Iterable
)

import docker
from docker.models.images import Image
from docker.models.containers import Container

from docker.errors import (
    BuildError,
    ImageNotFound,
    ImageLoadError,
    APIError
)
from psutil import (
    cpu_times
)

from psutil import (
    cpu_times
)


current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
path.append(libs)

from pylibs.mq.rabbit import MQ_TYPE
from pylibs.docker import (
    docker_client
)

def has_image(
    image_name: str = None
) -> bool:
    if image_name in [image.tags[0] for image in docker_client.images.list() if len(image.tags)>0]:
        return True
    else: return False

def has_container(
    container_name: str = None
) -> bool: 
    if container_name in container_list():
        return True
    else: return False

def image_list(
) -> list:
    return [image.tags[0] for image in docker_client.images.list() if len(image.tags)>0]

def container_list(
) -> list:
    return [container.name for container in docker_client.containers.list()]

def pull(
    image_name: str = None
) -> Image:
    if not has_image(image_name=image_name): 
        return docker_client.images.pull(
            repository=image_name.split(':')[0],
            tag=image_name.split(':')[-1]
        )


def logs(
    container: Container = None,
    stream: bool = None,
    follow: bool = None,
    wait: int = None,
    print_lines: bool = None,
    
) -> Union[bool, list]:
    log_lines = []
    stream = True if stream is None else stream
    follow = False if follow is None else follow
    wait = 10 if wait is None else wait

    sleep(wait)
    if has_container(container.name):
        if not stream:
            for line in docker_client.api.logs(
                container=container.name, 
                stream=stream, 
                follow=follow
            ).decode('utf-8').split("\n"):
                if line == '': continue
                log_lines.append(line)
        else:
            stream_lines = docker_client.api.logs(container=container.name, stream=stream, follow=follow)
            while True:
                try: 
                    stream_line = next(stream_lines).decode('utf-8')
                    log_lines.append(stream_line)
                except StopIteration as err:
                    print('log lines complete')
                    break
        if print_lines: print(dumps(
            log_lines,
            indent=2
        ))
        return log_lines
    else: return False

def build(
    image_tag: str = None,
    build_dir: str = None,
    dockerfile: str = None,
    buildargs: dict = None,
    decode: bool = None
) -> Union[tuple, bool]:
    image_tag: str = "local:latest" if image_tag is None else image_tag
    build_dir: str = join(libs, 'pylibs', 'docker') if build_dir is None else build_dir
    dockerfile: str = "Dockerfile" if dockerfile is None else dockerfile
    buildargs: dict = dict() if buildargs is None else buildargs
    decode = True if decode is None else decode
    if exists(join(build_dir, dockerfile)):
        filebytes: BytesIO = BytesIO(open(join(build_dir, dockerfile)).read().encode('utf-8'))
        #print(build_dir)
        try:
            image, build_generator = docker_client.images.build(
                path=build_dir,
                #fileobj=filebytes,
                dockerfile=dockerfile,
                rm=True,
                #forcerm=False,
                tag=image_tag,
                nocache=True,
                #pull=False,
                buildargs=buildargs,   
            )
            print(image.id)
            
            return image, build_generator
        except BuildError as err: 
            print(f"error during build {err}")
        except APIError as err:
            print(f"api error during build {err}")
    else: return False

def buildlogs(
    generator: Iterable = None,
    wait: int = None
):  
    wait: int = 10 if wait is None else wait
    sleep(wait)
    build_lines = []
    while True:
        try:
            line = next(generator)#.decode('utf-8').strip()
            #print(type(line))
            #print(line.keys())
            if 'stream' in line:
                txt = line['stream']
            #print()
            #txt = line['stream']
                if txt == "\n": continue
            
                build_lines.append(txt)
        except StopIteration as err:
            print('read through build log')
            break

    return build_lines

def run(
    image_name: str = None,
    ports: dict = None,
    environment: dict = None,
    command: str = None,
    privileged: bool = True,
    container_wait: int = 5,
) -> Union[Container, bool]:
    print('ports: ', ports)
    if not has_image(image_name=image_name):
        try:
            image = pull(image_name=image_name)
            print(f"downloaded missing image: {image.tags[0] if len(image.tags)>0 else image.id}")
            if ports is None:
                cont = docker_client.containers.run(
                    image=image_name,
                    command= "" if command is None else command,
                    detach=True,
                    hostname=image_name.split(':')[0],
                    name=image_name.split(':')[0],
                    remove=True,
                    environment= {"foo": "bar"} if environment is None else environment,
                    privileged=privileged
                )
            else:
                cont = docker_client.containers.run(
                    image=image_name,
                    command= "" if command is None else command,
                    detach=True,
                    hostname=image_name.split(':')[0],
                    name=image_name.split(':')[0],
                    remove=True,
                    environment= {"foo": "bar"} if environment is None else environment,
                    ports=ports,
                    privileged=privileged
                ) 

            log = logs(container=cont)
            return cont
        except ImageNotFound as err:
            print(f"error downloading image {err}")
            return False
        except APIError as err:
            print(f"api error thrown {err}")
            return False
    else:
        try:
            if ports is None:
                cont = docker_client.containers.run(
                    image=image_name,
                    command= "" if command is None else command,
                    detach=True,
                    hostname=image_name.split(':')[0],
                    name=image_name.split(':')[0],
                    remove=True,
                    environment= {"foo": "bar"} if environment is None else environment,
                    privileged=privileged
                )
            else:
                cont = docker_client.containers.run(
                    image=image_name,
                    command= "" if command is None else command,
                    detach=True,
                    hostname=image_name.split(':')[0],
                    name=image_name.split(':')[0],
                    remove=True,
                    environment= {"foo": "bar"} if environment is None else environment,
                    ports=ports,
                    privileged=privileged
                ) 
            log = logs(container=cont)

            return cont
        except ImageLoadError as err:
            print(f"error running container")
            return False
        except APIError as err:
            print(f"api error thrown")
            return False

def stop(
    container_name: str = None
) -> bool:
    if has_container(container_name=container_name):
        print(f"stopping container {container_name}")
        docker_client.containers.get(container_name).stop()

        if not has_container(container_name=container_name):
            return True
        else: return False
    else: 
        print(f"no container exists named {container_name}")
        return False
    
def rmi(
    image_name: str = None,
    force: bool = None,
) -> bool:
    force = True if force is None else force
    if not has_image(image_name=image_name):
       return True
    else:
        docker_client.images.remove(image=image_name, force=force) 
        if not has_image(image_name=image_name): 
            return True
        else: return False
