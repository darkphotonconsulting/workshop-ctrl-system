# Program Settings Files

In order to provide a version control safe mechanism of storing authentication, the HeadUnit backend (python) uses this settings directory. 

By default, *ONLY* this markdown file is checked in, and `.gitignore` is configured with the line:

```sh
settings/*.json
```

The ConfigLoader class is responsible for loading up any json files you drop here appropriately, you just need to tell it which file to use by setting the OS variable `CONFIG_PATH` when using it.

## File Format

The file type expected is JSON format, aside from this it's structure can be as arbitrary as needed, don't get crazy though, the written code expects some things to be stable.

### Database configuration

```json
{
    "database": {
        "mongo_host": "mongo.darkphotonworks-labs.io",
        "mongo_port": 27017,
        "mongo_username": "username",
        "mongo_password": "password"
    }
}
```

### Additional configurations accepted

- define what host and port the metrics and pi_service operate on. 

```json

{
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

Where applicable, the config loader will be exposed with `[--config-loader <config_file>]`
