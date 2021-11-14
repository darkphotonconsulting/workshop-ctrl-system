"""ORM Schemas
"""
from enum import unique
import json
import bson
from copy import copy
from pymongo.database import Database
from mongoengine import (
    Document,
    EmbeddedDocument
)
from mongoengine import (
    StringField,
    EmbeddedDocumentField,
    IntField,
    FloatField,
    DateTimeField,
    ListField,
    BooleanField
)

from graphene import (Int, Schema, List, ObjectType)
from graphene.relay import Node
from graphene_mongo import (
    MongoengineConnectionField,
    MongoengineObjectType
)

# class SystemTemperatureStats(Document):
#     label = StringField()
#     current = FloatField()
#     timestamp = 
class SystemMetricDiskUsageStats(Document):
    meta = {
        'collection': 'metrics-system-diskusage'
    }

    #"bytes_sent": 822508822, "bytes_recv": 822508822, "packets_sent": 3840450, "packets_recv": 3840450, "errin": 0, "errout": 0, "dropin": 0, "dropout": 0, "nic": "lo", "timestamp": 1636899341.879417}
    total = IntField()
    used = IntField()
    free = IntField()
    percent = FloatField()
    mountpoint = StringField()
    timestamp = FloatField()
class SystemMetricNetIOStats(Document):
    meta = {
        'collection': 'metrics-system-netio'
    }

    #"bytes_sent": 822508822, "bytes_recv": 822508822, "packets_sent": 3840450, "packets_recv": 3840450, "errin": 0, "errout": 0, "dropin": 0, "dropout": 0, "nic": "lo", "timestamp": 1636899341.879417}
    bytes_sent = IntField()
    bytes_recv = IntField()
    packets_sent = IntField()
    packets_recv = IntField()
    errin = IntField()
    errout = IntField()
    dropin = IntField()
    dropout = IntField()
    nic = StringField()
    timestamp = FloatField()
class SystemMetricCPUStats(Document):
    #'{"ctx_switches": 444292751, "interrupts": 266221587, "soft_interrupts": 117437679, "syscalls": 0, "timestamp": 1636908347.275202}'
    meta = {
        'collection': 'metrics-system-cpustats'
    }
    ctx_switches = IntField()
    interrupts = IntField()
    soft_interrupts = IntField()
    syscalls = IntField()
    timestamp = FloatField()

class SystemMetricCPUTime(Document):
    #'[{"user": 80168.36, "nice": 1.07, "system": 27316.64, "idle": 1068411.83, "iowait": 3976.51, "irq": 0.0, "softirq": 489.19, "steal": 0.0, "guest": 0.0, "guest_nice": 0.0, "cpuid": 1, "timestamp": 1636908403.750539}, {"user": 80168.36, "nice": 1.07, "system": 27316.64, "idle": 1068411.83, "iowait": 3976.51, "irq": 0.0, "softirq": 489.19, "steal": 0.0, "guest": 0.0, "guest_nice": 0.0, "cpuid": 2, "timestamp": 1636908403.750539}, {"user": 80168.36, "nice": 1.07, "system": 27316.64, "idle": 1068411.83, "iowait": 3976.51, "irq": 0.0, "softirq": 489.19, "steal": 0.0, "guest": 0.0, "guest_nice": 0.0, "cpuid": 3, "timestamp": 1636908403.750539}, {"user": 80168.38, "nice": 1.07, "system": 27316.65, "idle": 1068411.83, "iowait": 3976.51, "irq": 0.0, "softirq": 489.19, "steal": 0.0, "guest": 0.0, "guest_nice": 0.0, "cpuid": 4, "timestamp": 1636908403.750539}]'
    meta = {
        'collection': 'metrics-system-cputime'
    }
    user = FloatField()
    nice = FloatField()
    system = FloatField()
    idle = FloatField()
    iowait = FloatField()
    irq = FloatField()
    softirq = FloatField()
    steal = FloatField()
    guest = FloatField()
    guest_nice = FloatField()
    cpuid = IntField()
    timestamp = FloatField()

    
class SystemMetricVirtualMemory(Document):
    meta = {
        'collection': 'metrics-system-vmem'
    }
    #{"total": 8282419200, "available": 6776385536, "percent": 18.2, "used": 1402552320, "free": 5338615808, "active": 769622016, "inactive": 1995055104, "buffers": 221069312, "cached": 1320181760, "shared": 22982656, "slab": 124493824, "timestamp": 1636718116.904633}
    total = IntField()
    available = IntField()
    percent = FloatField()
    used = IntField()
    free = IntField()
    active = IntField()
    inactive = IntField()
    buffers = IntField()
    cached = IntField()
    shared = IntField()
    slab = IntField()
    timestamp = FloatField()

class SystemMetricSwap(Document):
    meta = {
        'collection': 'metrics-system-swap'
    }
    #{"total": 8282419200, "available": 6776385536, "percent": 18.2, "used": 1402552320, "free": 5338615808, "active": 769622016, "inactive": 1995055104, "buffers": 221069312, "cached": 1320181760, "shared": 22982656, "slab": 124493824, "timestamp": 1636718116.904633}
    total = IntField()
    used = IntField()
    free = IntField()
    percent = FloatField()
    sin = IntField()
    sout = IntField()
    timestamp = FloatField()

# relay class
class Relay(Document):
    """MongoEngine Schema for Relays

    Extends:
        Document (Document): MongoEngine Document type
    """
    meta = {
        'collection': 'static-relays'
    }
    model = StringField()
    state = BooleanField(required=True, default=False)
    description = StringField(required=True, unique=True)
    manufacturer = StringField(required=True, unique=False)
    #relay_channel = IntField(required=True, unique=True)
    #normally_open = BooleanField(required=True, unique=False)
    ac_voltage_max = IntField()
    ac_voltage_min = IntField()
    dc_voltage_max = IntField()
    dc_voltage_min = IntField()
    ac_amperage_min = IntField()
    ac_amperage_max = IntField()
    dc_amperage_min = IntField()
    dc_amperage_max = IntField()
    activation_type = StringField()
    activation_voltage = IntField()
    relay_channel = IntField(required=True,unique=True)
    normally_open = BooleanField(required=True)


class RelayGraphQL(MongoengineObjectType):
    class Meta:
        model = Relay
        interfaces = (Node,)
# define pin classes
class PinMap(EmbeddedDocument):
    """MongoEngine Schema for board_map key (embedded doc)

    Extends:
        Document (Document): MongoEngine Document type
    """
    gpio_bcm = IntField()
    physical_board = IntField()
    wiring_pi = IntField()
    uuid = StringField()


class PinData(EmbeddedDocument):
    """MongoEngine Schema for data key (embedded doc)

    Extends:
        Document (Document): MongoEngine Document type
    """
    title = StringField()
    descr = StringField()
    funcs = ListField(StringField())
    boardmap = EmbeddedDocumentField(PinMap)
    uuid = StringField()

class Pin(Document):
    """MongoEngine Schema for GPIOS (contains embedded doc types)

    Extends:
        Document (Document): MongoEngine Document type
    """
    meta = {
        'collection': 'static-gpios'
    }
    label = StringField()
    header_row = IntField()
    header_col = IntField()
    info_url = StringField()
    data = EmbeddedDocumentField(PinData)


class PinMapGraphQL(MongoengineObjectType):
    class Meta:
        model = PinMap
        interfaces = (Node, )


class PinDataGraphQL(MongoengineObjectType):
    class Meta:
        model = PinData
        interfaces = (Node, )


class PinGraphQL(MongoengineObjectType):
    class Meta:
        model = Pin
        interfaces = (Node,)





class System(Document):
    """MongoEngine Schema for System

    Extends:
        Document (Document): MongoEngine Document type
    """
    meta = {
        'collection': 'static-system'
    }
    manufacturer = StringField()
    system = StringField()
    released = StringField()
    model = StringField()
    revision = StringField()
    soc = StringField()
    pcb_revision = StringField()
    memory = IntField()
    storage = StringField()
    ethernet_speed = IntField()
    has_wifi = BooleanField()
    has_bluetooth = BooleanField()
    usb_ports = IntField()
    usb3_ports = IntField()
    board_headers = ListField()


class SystemGraphQL(MongoengineObjectType):
    class Meta:
        model = System
        interfaces = (Node, )



class Query(ObjectType):
    node = Node.Field()
    all_relays = MongoengineConnectionField(RelayGraphQL)
    all_gpios = MongoengineConnectionField(PinGraphQL)
    all_system = MongoengineConnectionField(SystemGraphQL)
    #role =


class GraphQLFactory():
    def __init__(self, query: Query, types: list):
        self.query = query
        self.types = types
        self.schema = Schema(
            query=self.query,
            types=self.types
        )