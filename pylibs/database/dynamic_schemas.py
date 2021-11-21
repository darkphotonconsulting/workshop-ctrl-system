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
    LongField,
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

MONGO_STRUCTURE = {
    'static': {
        'system': 'static-system',
        'gpios': 'static-gpios',
        'relays': 'static-relays',
        'all': ['static-system', 'static-gpios']
    },
    'dynamic': {
        'system_memory_stats': 'dynamic-system-memory-statistics',
        'system_net_stats': 'dynamic-system-network-statistics',
        'system_cpu_stats': 'dynamic-system-memory-statistics'
    }
}



class SystemMetricDiskUsageStats(Document):
    meta = {
        'collection': 'metrics-system-diskusage'
    }

    #"bytes_sent": 822508822, "bytes_recv": 822508822, "packets_sent": 3840450, "packets_recv": 3840450, "errin": 0, "errout": 0, "dropin": 0, "dropout": 0, "nic": "lo", "timestamp": 1636899341.879417}
    total = LongField()
    used = LongField()
    free = LongField()
    percent = IntField()
    mountpoint = StringField()
    timestamp = FloatField()


class SystemMetricDiskUsageStatsGraphQL(MongoengineObjectType):
    class Meta:
        model = SystemMetricDiskUsageStats
        interfaces = (Node,)
        
class SystemMetricNetIOStats(Document):
    meta = {
        'collection': 'metrics-system-netio'
    }

    #"bytes_sent": 822508822, "bytes_recv": 822508822, "packets_sent": 3840450, "packets_recv": 3840450, "errin": 0, "errout": 0, "dropin": 0, "dropout": 0, "nic": "lo", "timestamp": 1636899341.879417}
    bytes_sent = LongField()
    bytes_recv = LongField()
    packets_sent = LongField()
    packets_recv = LongField()
    errin = LongField()
    errout = LongField()
    dropin = LongField()
    dropout = LongField()
    nic = StringField()
    timestamp = FloatField()

class SystemMetricNetIOStatsGraphQL(MongoengineObjectType):
    class Meta:
        model = SystemMetricNetIOStats
        interfaces = (Node,)

class SystemMetricDiskUsageStatsGraphQL(MongoengineObjectType):
    class Meta:
        model = SystemMetricDiskUsageStats
        interfaces = (Node,)
        
class SystemMetricCPUStats(Document):
    #'{"ctx_switches": 444292751, "interrupts": 266221587, "soft_interrupts": 117437679, "syscalls": 0, "timestamp": 1636908347.275202}'
    meta = {
        'collection': 'metrics-system-cpustats'
    }
    ctx_switches = LongField()
    interrupts = LongField()
    soft_interrupts = LongField()
    syscalls = LongField()
    timestamp = FloatField()

class SystemMetricCPUStatsGraphQL(MongoengineObjectType):
    class Meta:
        model = SystemMetricCPUStats
        interfaces = (Node,)

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

class SystemMetricCPUTimeGraphQL(MongoengineObjectType):
    class Meta:
        model = SystemMetricCPUTime
        interfaces = (Node,)
    
class SystemMetricVirtualMemory(Document):
    meta = {
        'collection': 'metrics-system-vmem'
    }
    #{"total": 8282419200, "available": 6776385536, "percent": 18.2, "used": 1402552320, "free": 5338615808, "active": 769622016, "inactive": 1995055104, "buffers": 221069312, "cached": 1320181760, "shared": 22982656, "slab": 124493824, "timestamp": 1636718116.904633}
    total = LongField()
    available = LongField()
    percent = FloatField()
    used = LongField()
    free = LongField()
    active = LongField()
    inactive = LongField()
    buffers = LongField()
    cached = LongField()
    shared = LongField()
    slab = LongField()
    timestamp = FloatField()

class SystemMetricVirtualMemoryGraphQL(MongoengineObjectType):
    class Meta:
        model = SystemMetricVirtualMemory
        interfaces = (Node,)

class SystemMetricSwap(Document):
    meta = {
        'collection': 'metrics-system-swap'
    }
    #{"total": 8282419200, "available": 6776385536, "percent": 18.2, "used": 1402552320, "free": 5338615808, "active": 769622016, "inactive": 1995055104, "buffers": 221069312, "cached": 1320181760, "shared": 22982656, "slab": 124493824, "timestamp": 1636718116.904633}
    total = LongField()
    used = LongField()
    free = LongField()
    percent = FloatField()
    sin = LongField()
    sout = LongField()
    timestamp = FloatField()

class SystemMetricSwapGraphQL(MongoengineObjectType):
    class Meta:
        model = SystemMetricSwap
        interfaces = (Node,)

class Query(ObjectType):
    node = Node.Field()
    all_vmem = MongoengineConnectionField(SystemMetricVirtualMemoryGraphQL)
    all_swap = MongoengineConnectionField(SystemMetricSwapGraphQL)
    all_cputime = MongoengineConnectionField(SystemMetricCPUTimeGraphQL)
    all_cpustats = MongoengineConnectionField(SystemMetricCPUStatsGraphQL)
    all_diskusage = MongoengineConnectionField(SystemMetricDiskUsageStatsGraphQL)
    all_netio = MongoengineConnectionField(SystemMetricNetIOStatsGraphQL)


class GraphQLFactory():
    def __init__(self, query: Query, types: list):
        self.query = query
        self.types = types
        self.schema = Schema(
            query=self.query,
            types=self.types
        )

graphql = GraphQLFactory(
    Query, 
    [
        SystemMetricVirtualMemoryGraphQL, 
        SystemMetricSwapGraphQL, 
        SystemMetricCPUTimeGraphQL, 
        SystemMetricCPUStatsGraphQL,
        SystemMetricNetIOStatsGraphQL 
        ]
)