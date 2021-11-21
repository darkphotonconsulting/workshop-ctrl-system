from os.path import (
    dirname,
    abspath
)

from os import (
    environ,
    urandom
)
#import sys
from json import (
    loads
)
from sys import (
    stdout,
    stderr,
    path,
    modules
)

from flask_mongoengine import MongoEngine

current_dir = dirname(abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-4])
path.append(libs)
# set default configuration file 
if 'HEADUNIT_CONFIG' not in environ:
    environ['HEADUNIT_CONFIG'] = 'settings/config.json'

from pylibs.logging.loginator import Loginator

from pylibs.database.dynamic_schemas import (
    # Query, GraphQLFactory,
    SystemMetricCPUStats, SystemMetricCPUStatsGraphQL,
    SystemMetricCPUTime, SystemMetricCPUTimeGraphQL,
    SystemMetricVirtualMemory, SystemMetricVirtualMemoryGraphQL,
    SystemMetricSwap, SystemMetricSwapGraphQL,
    SystemMetricDiskUsageStats, SystemMetricDiskUsageStatsGraphQL,
    SystemMetricNetIOStats, SystemMetricNetIOStatsGraphQL
)

from graphene import (
    Int, 
    Schema, 
    List, 
    ObjectType
)
from graphene.relay import Node
from graphene_mongo import (
    MongoengineConnectionField,
    MongoengineObjectType
)

class Query(ObjectType):
    node = Node.Field()
    all_vmem = MongoengineConnectionField(SystemMetricVirtualMemoryGraphQL)
    all_swap = MongoengineConnectionField(SystemMetricSwapGraphQL)
    all_cputime = MongoengineConnectionField(SystemMetricCPUTimeGraphQL)
    all_cpustats = MongoengineConnectionField(SystemMetricCPUStatsGraphQL)
    all_diskusage = MongoengineConnectionField(SystemMetricDiskUsageStatsGraphQL)
    all_netio = MongoengineConnectionField(SystemMetricNetIOStatsGraphQL)


class GraphQLFactory():
    def __init__(self, 
        query: Query, 
        types: list
    ):
        self.query = query
        self.types = types
        self.schema = Schema(
            query=self.query,
            types=self.types
        )

db = MongoEngine()
graphql = GraphQLFactory(
    Query, 
    [
        SystemMetricVirtualMemoryGraphQL, 
        SystemMetricSwapGraphQL, 
        SystemMetricDiskUsageStatsGraphQL,
        SystemMetricCPUStatsGraphQL,
        SystemMetricCPUTimeGraphQL,
        # SystemMetricNetIOStats,
    ]
)