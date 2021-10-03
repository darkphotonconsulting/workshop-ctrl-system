import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(current_dir.split('/')[0:-1])

sys.path.append(libs)


from pylibs.schema.default_schemas import SchemaFactory, DynamicSchemas, StaticSchemas
from pylibs.coders.decode import SchemaTemplateDecoder
import json
print(json.loads(open('schemas/testing-gpios.json').read(),
    cls=SchemaTemplateDecoder))