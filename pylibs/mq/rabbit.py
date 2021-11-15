from flask import Flask
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
#import sys
from json import (
    loads,
    dumps,
)
from sys import (
    stdout,
    stderr,
    path,
    modules
)

from secrets import choice
import string



from typing import (
    Union,
    Any,
    Optional
)

from requests import (
    get,
    put,
    post,
    patch,
    delete,
)

from urllib.parse import (
    urljoin,
    urlparse
)
from pika import (
    BlockingConnection,
    ConnectionParameters,
)

from pika.exceptions import (
    ChannelClosed,
)
from pika.adapters.blocking_connection import (
    BlockingChannel,
)

from pika.frame import (
    Method,
)
from pika.spec import (
    Connection,
    Queue,
)

current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
path.append(libs)


from pylibs.config.configuration import ConfigLoader, Configuration


MQ_TYPE = 'rabbitmq'
MQ_HOST = 'localhost'
MQ_PORT = 5672
MQ_ADMIN_PORT = 15672
MQ_SOCKET_TIMEOUT = 60*60

        
def broker_connect(
    broker_host: str = None,
    broker_port: int = None,
    broker_vhost: str = None
) -> BlockingConnection:
    broker_host: str = MQ_HOST if broker_host is None else broker_host 
    broker_vhost: str = '/' if broker_vhost is None else broker_vhost
    broker_port: int = MQ_PORT if broker_port is None else broker_port
    return BlockingConnection(
        ConnectionParameters(
            host=broker_host, 
            port=broker_port,
            virtual_host=broker_vhost,
        )
    )

def open_channel(
    conn: BlockingConnection = None     
) -> Union[BlockingChannel, bool]:
    conn = broker_connect() if conn is None else conn
    if conn.is_open:
        return conn.channel()
    else: return False

def create_queue(
    conn: BlockingConnection = None,
    channel: BlockingChannel = None,
    queue: str = None,
    passive: bool = None,
    durable: bool = None
) -> Method:
    conn = broker_connect() if conn is None else conn
    channel = open_channel(conn=conn) if channel is None else channel
    queue = "default" if queue is None else queue
    durable = True if durable is None else durable
    passive = True if passive is None else passive
    if channel.is_open:
        try:
            return channel.queue_declare(
                queue=queue,
                passive=passive,
                durable=durable,
            )
        except ChannelClosed as err:
            print(f"error checking for or creating queue {queue} {err}")
            return False

def publish_message(
    conn: BlockingConnection = None,
    channel: BlockingChannel = None,
    exchange: str = '',
    queue: Union[Method, str] = None,
    message: Any = None,
):
    conn = broker_connect() if conn is None else conn
    channel = open_channel(conn=conn) if channel is None else channel
    message = "hello world" if message is None else message
    if queue is not None:
        queue = queue.method.queue if isinstance(queue, Method) else create_queue(channel=channel, queue=queue, passive=False).method.queue
    else:
        queue = create_queue(passive=False).method.queue

    return channel.basic_publish(
        exchange=exchange,
        routing_key=queue,
        body=message,
    )
    

class RabbitAdmin(object):
    def __init__(
        self,
        broker_mgmt_host: str = None,
        broker_mgmt_port: int = None,
        broker_mgmt_user: str = None,
        broker_mgmt_password: str = None,
        broker_mgmt_vhost: str = None
    ) -> None:
        print(f"{MQ_TYPE}")
        
        self.broker_mgmt_host: str = MQ_HOST if broker_mgmt_host is None else broker_mgmt_host 
        self.broker_mgmt_port: int = MQ_ADMIN_PORT if broker_mgmt_port is None else broker_mgmt_port
        self.broker_mgmt_vhost = '' if broker_mgmt_vhost is None else broker_mgmt_vhost
        self.broker_mgmt_user = 'guest' if broker_mgmt_user is None else broker_mgmt_user
        self.broker_mgmt_password = 'guest' if broker_mgmt_password is None else broker_mgmt_password
        self.manager: str = f"http://{self.broker_mgmt_host}:{self.broker_mgmt_port}/{self.broker_mgmt_vhost}"

    def list_queues(
        self,
    ) -> dict:
        response = get(urljoin(base=self.manager, url='api/queues'), auth=(self.broker_mgmt_user, self.broker_mgmt_password))
        return [q for q in response.json()]

    def list_vhosts(
        self,
    ) -> dict:
        response = get(urljoin(base=self.manager, url='api/vhosts'), auth=(self.broker_mgmt_user, self.broker_mgmt_password))
        return [vhost for vhost in response.json()]

    def create_vhost(
        self,
        vhost_name: str = None
    ) -> bool:
        response = put(urljoin(base=self.manager, url=f"api/vhosts/{vhost_name}"), auth=(self.broker_mgmt_user, self.broker_mgmt_password))
        if vhost_name in [vhost['name'] for vhost in self.list_vhosts()]:
            return True 
        else: return False

    def delete_vhost(
        self,
        vhost_name: str = None
    ) -> bool:
        response = delete(urljoin(base=self.manager, url=f"api/vhosts/{vhost_name}"), auth=(self.broker_mgmt_user, self.broker_mgmt_password))
        if vhost_name in [vhost['name'] for vhost in self.list_vhosts()]:
            return False 
        else: return True

    def list_nodes(
        self,
    ) -> dict:
        response = get(urljoin(base=self.manager, url='api/nodes'), auth=(self.broker_mgmt_user, self.broker_mgmt_password))
        return [node for node in response.json()]

    def node_memory(
        self,
        node_name: str = None
    ):
        node_name = "rabbit@new" if node_name is None else node_name
        node = [node for node in self.list_nodes() if node['name'] == node_name][0]
        response = get(
            urljoin(
                base=self.manager, 
                url=f"api/nodes/{node['node_name']}/memory"
            ), 
            auth=(
                self.broker_mgmt_user, 
                self.broker_mgmt_password
            )
        )
        return response.json()
        
    
class Rabbit(object):
    
    def __init__(self,
        broker_host: str = None,
        broker_port: int = None,
        broker_vhost: str = None,
        broker_timeout: int = None,
        broker_channel: int = None,
        broker_admin: RabbitAdmin = None
    ) -> None:
        self.broker_host: str = MQ_HOST if broker_host is None else broker_host 
        self.broker_vhost: str = '/' if broker_vhost is None else broker_vhost
        self.broker_port: int = MQ_PORT if broker_port is None else broker_port
        self.broker_timeout: int = MQ_SOCKET_TIMEOUT if broker_timeout is None else broker_timeout
        self.admin = RabbitAdmin() if broker_admin is None else broker_admin
        self.broker: BlockingConnection = BlockingConnection(
            ConnectionParameters(
                host=self.broker_host, 
                port=self.broker_port,
                virtual_host=self.broker_vhost,
                socket_timeout=self.broker_timeout,
                #blocked_connection_timeout=self.broker_timeout
            )
        )
        self.channel: BlockingChannel = self.broker.channel() if broker_channel is None else self.broker.channel(channel_number=broker_channel)

    def queue(self,
        queue: str = None,
        passive: bool = None,
        durable: bool = None 
    ) -> Union[Method, bool]:
        passive = False if passive is None else passive
        durable = True if durable is None else durable
        
        if queue is None: return False
        
        if self.channel.is_open:
            try:
                q = self.channel.queue_declare(
                    queue=queue,
                    passive=passive,
                    durable=False if durable is None else durable,
                )
                return q
            except ChannelClosed as err:
                print(f"the queue {queue} already exists")
                return False
        else: return False

    def publish_message(
        self,
        exchange: str = None,
        queue: Union[Method, str] = None,
        message: Any = None,
    ) -> Union[Method, bool]:
        channel = self.channel
        exchange = '' if exchange is None else exchange
        channel =  self.broker.channel() if self.channel.is_closed else channel
        queues = [q['name'] for q in self.admin.list_queues()]
        if queue is not None:
            # check if q exists
            if isinstance(queue, Method):
                queue = queue.method.queue
            elif isinstance(queue, str):
                queue = queue

            if queue not in queues:    
                queue = self.queue(queue=queue).method.queue
        else:
            queue_name = ''.join([choice(string.ascii_uppercase + string.digits) for _ in range(10)])
            queue = create_queue(queue=queue_name,passive=False).method.queue

        message = "hello world" if message is None else message

        if isinstance(message, str):
            message = message
        elif isinstance(message, (dict, list)):
            message = dumps(message)

        print(f"queue is {queue}")

        return channel.basic_publish(
            exchange=exchange,
            routing_key=queue,
            body=message,
        )

    
