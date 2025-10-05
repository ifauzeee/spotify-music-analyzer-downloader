import configparser
import os

config = configparser.ConfigParser()

if os.path.exists('config.ini'):
    config.read('config.ini')
else:
    # Default fallback values
    config['Analysis'] = {'similarity_threshold': '85'}
    config['Cache'] = {'expiration_hours': '24'}

def get_config_value(section, key, type='int'):
    try:
        if type == 'int':
            return config.getint(section, key)
        elif type == 'float':
            return config.getfloat(section, key)
        else:
            return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        # Fallback to default if not found
        if key == 'similarity_threshold': return 85
        if key == 'expiration_hours': return 24
        return None