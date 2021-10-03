from pylibs.schema.orm_schemas import PinMap, System, Relay, Pin
import mongoengine
from mongoengine import connect
from backend.config import DevelopmentConfig, ProductionConfig
from mongoengine import (Document, EmbeddedDocument)
from mongoengine import (StringField, EmbeddedDocumentField, IntField,
                         DateTimeField, ListField, BooleanField, ReferenceField, GenericReferenceField, EnumField)
from pymongo.errors import (
    DuplicateKeyError
)
from mongoengine.errors import (
    NotUniqueError
)

config = ProductionConfig(mongo_username='root',mongo_password='toor')
mongo_connection_string = config.mongo_connect_string
connection = connect(host=f"{mongo_connection_string}/static")



class UsedPins(Document):
    """MongoEngine Schema for Relays

    Extends:
        Document (Document): MongoEngine Document type
    """
    meta = {'collection': 'static-used-gpios'}
    gpio_bcm = IntField()
    pin_data = ReferenceField(Pin)

class ConfiguredRelayChannel(Document):
    """MongoEngine Schema for Relays

    Extends:
        Document (Document): MongoEngine Document type
    """
    meta = {'collection': 'static-configured-relay-channels'}
    gpio_bcm = IntField(required=True, unique=True)
    pin = ReferenceField(Pin)
    relay = ReferenceField(Relay)







pinobjs = [i for i in Pin.objects(__raw__={'data.boardmap.gpio_bcm': {'$eq': 17}})]

relayobjs = [i for i in Relay.objects()]
#print(pinobjs[0])

# example.. 
# user selects GPIO pin 17
pinobj = pinobjs[0]
# user selects relay channel 1
relayobj = relayobjs[0]
configured_relay = ConfiguredRelayChannel(
gpio_bcm = 17,
pin = pinobj,
relay = relayobj
)


try:
    configured_relay.save()
except NotUniqueError as error_message:
    print('already created')
except DuplicateKeyError as error_message:
    print('already created')
finally:
    print([i.to_json() for i in ConfiguredRelayChannel.objects(pin__in=[pinobj])])