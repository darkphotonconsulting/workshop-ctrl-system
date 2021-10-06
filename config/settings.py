class Config(object):
    """Config

    This is a naïve configuration object and largely not used
    """
    raspi_service_host = '0.0.0.0'
    raspi_service_port = 5001
    metrics_service_host = '0.0.0.0'
    metrics_service_port = 5002
    mongodb_host = '127.0.0.1'
    mongodb_port = 27017
    mongodb_database = 'headunit-v1'
    # database.collection.schema
    mongodb_schema = {
        'pi-data': {
            'pi-system': {
            },
            'pi-cpu': {},
            'pi-mem': {},
            'pi-io': {},
            'pi-net': {},
            'gpio-system': {},
            'gpio-state': {}
        }
    }