import os, sys

from loguru import logger
import gila
from copy import copy
from os import environ


def load_config(config_file, debug=False):
    if not os.path.exists(config_file):
        logger.error("configuration file not found")
        sys.exit(1)
    path = os.path.dirname(os.path.abspath(config_file))
    file_name = os.path.basename(os.path.abspath(config_file))
    file_name = os.path.splitext(file_name)[0]
    config = Config.instance(debug, path, file_name)
    return config


class SensorObjet(object):
    def __init__(self, data):
        self.__data__ = copy(data)

    @property
    def type(self):
        return self.__data__.get("type")

    @property
    def port(self):
        return self.__data__.get("port")

    @property
    def name(self):
        return self.__data__.get("sensorName")

    @property
    def instance(self):
        return self.__data__.get("instanceName")

class SensorConfig(object):
    sflow_sensors = []
    netflow_sensors = []
    def __init__(self, sensors):
        for key in sensors:
            o = SensorObjet(key)
            if o.type == "sflow":
                self.sflow_sensors.append(o)
            else:
                self.netflow_sensors.append(o)

class PmfAcctConfig(object):
    def __init__(self, **kwargs):
        self.accepted_types = ["netflow", "sflow"]
        self.__config__ = copy(kwargs)

    def is_valid(self, requested_type):
        return requested_type in self.accepted_types

    def config_file(self, requested_type):
        if self.is_valid(requested_type):
            return self.__config__.get('config')

    @property
    def types(self):
        return self.accepted_types

    def image(self, requested_type):
        if self.is_valid(requested_type):
            return self.__config__.get('image')

    @property
    def netflow_config(self):
        return self.__config__.get('netflow', {})

    @property
    def sflow_config(self):
        return self.__config__.get('sflow', {})

class Config(object):
    __instance__ = None
    __config__ = {}
    __pmfconfig__ = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @property
    def environment(self):
        return self.__config__.get('environment_file', '.env')

    @classmethod
    def load_config(cls):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        gila.set_default('paths.template_dir', './conf/')
        gila.set_default('paths.template_dir', "templates")

    @classmethod
    def instance(cls, debug=False, config_path='./conf', config_file='app.yaml'):
        if cls.__instance__ is None:
            logger.debug('Creating new configuration instance')
            cls.__instance__ = cls.__new__(cls)

            cls.load_config()

            gila.set_config_name(config_file)
            gila.automatic_env()
            gila.add_config_path(config_path)
            gila.read_config_file()

            ## allow CLI override
            if debug:
                gila.override('debug', debug)
            config_data = gila.all_config()
            cls.__pmfconfig__ = PmfAcctConfig(**config_data.get("pmacct", {}))
            cls.__sensors__ = SensorConfig(config_data.get("sensors", {}))


        return cls.__instance__