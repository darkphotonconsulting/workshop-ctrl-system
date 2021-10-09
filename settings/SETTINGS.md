# TOC

- [TOC](#toc)
  - [Program Settings Files](#program-settings-files)
  - [File Format](#file-format)
    - [Configuration Schema](#configuration-schema)
    - [A configuration exampe](#a-configuration-exampe)
    - [Using ConfigLoader](#using-configloader)
      - [In Scripts](#in-scripts)
      - [In Code](#in-code)

## Program Settings Files

In order to provide a version control safe mechanism of storing authentication, the HeadUnit backend (python) uses this settings directory.

By default, *ONLY* this markdown file is checked in, and `.gitignore` is configured with the line:

```sh
settings/*.json
```

The ConfigLoader class is responsible for loading up any json files you drop here appropriately, you just need to tell it which file to use by setting the OS variable `CONFIG_PATH` when using it.

## File Format

The file type expected is JSON format.

### Configuration Schema

```json
{
    "database": {
        "mongo_host": str,
        "mongo_port": int,
        "mongo_username": str,
        "mongo_password": str
    },
    "metrics": {
        "service_host": str,
        "service_port": int
    },
    "pi": {
        "service_host": str,
        "service_port": int
    }
}
```

### A configuration exampe

```json
{
    "database": {
        "mongo_host": "mongo.io.com",
        "mongo_port": 27017,
        "mongo_username": "superuser",
        "mongo_password": "myhardpassword"
    },
    "metrics": {
        "metrics_host": "0.0.0.0",
        "metrics_port": 5000,
    },
    "pi_service": {
        "pi_service_host": "0.0.0.0",
        "pi_service_port": 5001
    }
}
```

### Using ConfigLoader

#### In Scripts

Where applicable, ConfigLoader is enabled with `[--config-loader <config_file>]`

#### In Code

```python
from copy import copy
from config.config_loader import ConfigLoader
config = ConfigLoader(from_file=True, config='./settings/config-dev.json').add_attributes()

# access your config
config.config 

# access your data like this
config.mongo_username 

# or like this
config.get_key('mongo_username')

# or like this
config.config['mongo_username']

# reset your config
config.set_config(from_string=True, '{"database": {"mongo_host": "127.0.0.1", "mongo_port": 27017, "mongo_username": "foo", "mongo_password": "bar"}}')

```
