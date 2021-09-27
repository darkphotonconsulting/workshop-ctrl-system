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
    board_port = IntField(required=True, unique=True),
    gpio_port = IntField(required=True, unique=True)
    state = BooleanField(required=True, default=False)


# define pin classes
class PinMap(EmbeddedDocument):
    """MongoEngine Schema for board_map key (embedded doc)

    Extends:
        Document (Document): MongoEngine Document type
    """
    gpio_bcm = StringField(primary_key=True)
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