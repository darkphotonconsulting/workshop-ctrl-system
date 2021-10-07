import os
import sys 

current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-2])
print(libs)
sys.path.append(libs)

from mongoengine import (
    Document,
    EmbeddedDocument,
    DynamicEmbeddedDocument
)
from mongoengine import (
    StringField,
    IntField,
    BooleanField,
    DateTimeField,
    ListField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    DynamicField
)

from pylibs.schema.default_schemas import SchemaFactory


schema_factory = SchemaFactory()

system = schema_factory.get_default_schema_template(
    schema_type='static',
    schema_template_name='system'
)
gpios = schema_factory.get_default_schema_template(
    schema_type='static',
    schema_template_name='gpios'
)

def class_factory(
    class_name: str = None,
    base_classes: list = [Document],
    fields: dict = None,
):
    klass = type(
        class_name,
        tuple(base_classes),
        fields,
    )
    return klass


def field_from_template_value(key,value):
    if value is str:
        return (key, StringField())
    elif value is int:
        return (key, IntField())
    elif value is bool:
        return (key, BooleanField())
    elif value is list:
        return (key, ListField())
    elif value is dict:
        return (key, EmbeddedDocumentField())
    else:
        return (key, DynamicField())


def fields_from_schema_template(
    schema_template: dict = None,
    fields: list = None,
    embedded_fields: list = None
):
    if fields is None:
        fields = []
    if embedded_fields is None:
        embedded_fields = []
        
    for key, value in schema_template.items(): # iterate each key and value at this level of the schema

        #print(f"key: {key} value: {value} type: {type(value)}")
        if value in [str, int, list, bool]:
            fields.append(
                field_from_template_value(key=key, value=value)
            )
            #return fields
        if isinstance(value, dict): #recurse into the dict value
            fields.append(fields_from_schema_template(schema_template=value))
            return fields
            #return fields
        # else: #setup 
        #     fields.append(field_from_template_value(key=key, value=value))
        #     print(fields)
            #return fields
    return fields


my_fields = fields_from_schema_template(
    schema_template=gpios,   
)

print(my_fields)
