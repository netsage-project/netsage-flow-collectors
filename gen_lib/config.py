import os, sys

from loguru import logger
import gila
from copy import copy
from gen_lib.sensors import SensorObjet
from os import environ


def load_config(config_file, debug=False):
    if not os.path.exists(config_file):
        logger.error("configuration file not found")
        sys.exit(1)
    path = os.path.dirname(os.path.abspath(config_file))
    file_name = os.path.basename(os.path.abspath(config_file))
    file_name = os.path.splitext(file_name)[0]
    Config.instance(debug, path, file_name)


class SensorConfig(object):
    sflow_sensors = []
    netflow_sensors = []

    def __init__(self, sensors):
        ports = set()
        for key in sensors:
            o = SensorObjet(key)
            if o.enabled is False:
                continue
            if o.port in ports:
                raise Exception(
                    "invalid configuration.  Port {} is already used with a different configuration".format(o.port))
            if o.type == "sflow":
                self.sflow_sensors.append(o)
                ports.add(o.port)
            else:
                self.netflow_sensors.append(o)
                ports.add(o.port)


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
    def dev_mode(self):
        return gila.get("include_dev_generate")

    @property
    def environment(self):
        return gila.get('environment_file')

    @property
    def deploy_path(self):
        return gila.get('deployment_location')

    @property
    def template_folder(self):
        return gila.get('template_folder')

    def template_path(self, template_type, file):
        return os.path.join(self.template_folder, gila.get("template_locations.{}".format(template_type)), file)

    @property
    def sensors(self):
        return self.__sensors__

    @property
    def pmacct_config(self):
        return self.__pmfconfig__

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
            cls.__config__ = gila.all_config()
            cls.__pmfconfig__ = PmfAcctConfig(**cls.__config__.get("pmacct", {}))
            cls.__sensors__ = SensorConfig(cls.__config__.get("sensors", {}))

        return cls.__instance__
