from yaml import load
from bunch import bunchify, Bunch
from utils.nesting_exception import NestingException

def load_settings(settings_filename):
    settings = bunchify(load(file(settings_filename)))
    return Bunch(sources_filename=settings.sources_filename,
                 logging_config_filename=settings.logging_config_filename,
                 oxtalks_username=settings.oxtalks.username,
                 oxtalks_password=settings.oxtalks.password,
                 oxtalks_hostname=settings.oxtalks.hostname)

class SettingsError(NestingException):
    pass
