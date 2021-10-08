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

# development, testing
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
####

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
        return StringField()
    elif value is int:
        return IntField()
    elif value is bool:
        return BooleanField()
    elif value is list:
        return ListField()
    elif value is dict:
        return EmbeddedDocumentField()
    else:
        return DynamicField()


def fields_from_schema_template(
    schema_template: dict = None,
    field_data: dict = None,
):
    if field_data is None:
        field_data = {}

    if isinstance(schema_template, dict):
        for key, value in schema_template.items(): # iterate each key and value at this level of the schema
            if value in [str, int, list, bool]:
                field_data[key] = field_from_template_value(key=key,
                                                            value=value)
            elif isinstance(value, dict):  #recurse into the dict value
                field_data[key] = {}
                field_data[key] = fields_from_schema_template(
                    schema_template=value)
    return field_data

def classes_from_schema_template(
    schema_template: dict = None,
    base_classes: list = None,
    classes: dict = None,
    class_name: str = None,
    class_name_prefix: str = None,
    fields: dict = None,
):
    """classes_from_schema_template Returns a list of dynamically generated mongoengine Document classes that represent the provided schema
    

    Example:

    Nested Template Example (gpios)

    Inputs:
    
        ```
            {
                'data': {
                    'title': str,
                    'descr': str,
                    'funcs': list,
                    'boardmap': {
                        'physical_board': str, 
                        'gpio_bcm': str, 
                        'wiring_pi': str
                    },
                    'header_col': int,
                    'header_row': int,
                    'label': str
                }
            }
        ```

    Process:
    
        Decoding this template to classes looks something like:

        import pylibs.schema.factory
        from pylibs.schema.default_schemas import SchemaFactory
        schema_factory = SchemaFactory()
        gpios = schema_factory.get_default_schema_template(
            schema_type='static',
            schema_template_name='gpios'
        )
        gpio_classes  = pylibs.schema.factory.classes_from_schema_template(
            schema_template=gpios,
        )

    Outputs:
    
        In [0]: gpio_classes
        Out[0]: 
        {
            'Data': {
                'Data': mongoengine.base.metaclasses.Data,
                'Boardmap': {
                    'Boardmap': mongoengine.base.metaclasses.Boardmap
                }
            }
        }

        In [1]: gpio_classes['Data']['Boardmap']['Boardmap']
        Out[1]: mongoengine.base.metaclasses.Boardmap

        In [2]: BoardMap.__name__
        Out[2]: 'Boardmap'

        In [3]: BoardMap.wiring_pi
        Out[3]: <mongoengine.fields.StringField at 0xb217e350>
        
        
        

        
    Outputs

    class DataUserDocument(Document):
        title = StringField()
        ...

    class BoardmapDocument(DataUserDocument)
        wiring_pi = IntField()
        ...

    Args:
        schema_template (dict, optional): [description]. Defaults to None.
        base_classes (list, optional): [description]. Defaults to None.
        classes (list, optional): [description]. Defaults to None.
        class_name_prefix (str, optional): [description]. Defaults to None.
        fields (dict, optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    if class_name is None:
        class_name = ""
    if base_classes is None:
        base_classes = [Document]
    if classes is None:
        classes = {}

    if isinstance(schema_template, dict): #the schema_template object is a dict
        for key, value in schema_template.items():
            if value in [str, int, bool, list]: # keys are not dict values

                #print(f"{class_name} {class_name_prefix}")
                fields = fields_from_schema_template(schema_template=schema_template)
                class_title = f"{class_name_prefix.capitalize() if class_name_prefix is not None else ''}{class_name.capitalize()}"
                print(
                    f"non-dict branch: current_class  '{class_title}' ->  existing classes  '{list(classes.keys())}'  <- on key: '{key}' with value '{value}'"
                )
                #print(f"class title is: {class_title}")
                classes[class_name.capitalize()] = class_factory(
                    class_name=class_title,
                    base_classes=base_classes,
                    fields=fields)
            if isinstance(value, dict): # value is a dict, the current class should have an embedded field representing the "embedded class"
                fields = fields_from_schema_template(schema_template=value)
                class_title = f"{class_name_prefix.capitalize() if class_name_prefix is not None else ''}{key.capitalize()}"
                print(
                    f"dict branch: current_class  '{class_title}' ->  existing classes  '{list(classes.keys())}'  <- on key: '{key}' with value '{value}'"
                )

                if len(
                        list(classes.keys())
                ) > 0:  # the "parent" class is the last class seen, add an attibute linking key = EmbeddedDocumentField(<lastClass>)
                    last_key = list(classes.keys())[-1]
                    parent_class = classes[last_key]
                    print(f"parent class: {parent_class.boardmap}")



                classes[key.capitalize()] = classes_from_schema_template(
                    schema_template=value,
                    base_classes=[
                        EmbeddedDocument,
                    ],
                    fields=fields,
                    class_name=class_title,
                )

                #print('ok...')
    return classes



# my_fields = fields_from_schema_template(
#    schema_template=gpios,
# )

# print(gpios)
# print(my_fields)
# print(type(my_fields))
