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
    DateTimeField,
    ListField,
    BooleanField
)

from graphene import (Schema, List, ObjectType)
from graphene.relay import Node
from graphene_mongo import (
    MongoengineConnectionField,
    MongoengineObjectType
)


# relay class
class Relay(Document):
    """MongoEngine Schema for Relays

    Extends:
        Document (Document): MongoEngine Document type
    """
    meta = {
        'collection': 'static-relays'
    }
    relay_channel = IntField(required=True,unique=True)
    description = StringField(required=True, unique=True)
    normally_open = BooleanField(required=True)
    board_port = IntField(required=True, unique=True)
    gpio_port = IntField(required=True, unique=True)
    state = BooleanField(required=True, default=False)

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
    gpio_bcm = StringField()
    physical_board = StringField()
    wiring_pi = StringField()


class PinData(EmbeddedDocument):
    """MongoEngine Schema for data key (embedded doc)

    Extends:
        Document (Document): MongoEngine Document type
    """
    title = StringField()
    descr = StringField()
    funcs = ListField()
    boardmap = EmbeddedDocumentField(PinMap)


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