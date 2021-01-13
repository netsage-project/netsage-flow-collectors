import os
import sys

from loguru import logger
import gila
from copy import copy
from gen_lib.sensors import SensorObjet
from os import environ


def load_config(config_file, debug=False):
    """
    Load the configuration file into the Config instance
    """
    if not os.path.exists(config_file):
        logger.error("configuration file not found")
        sys.exit(1)
    path = os.path.dirname(os.path.abspath(config_file))
    file_name = os.path.basename(os.path.abspath(config_file))
    file_name = os.path.splitext(file_name)[0]
    Config.instance(debug, path, file_name)


class SensorConfig(object):
    """
    Encapsulate all the sensors define and performs sanity checks
    on configuration.

    Also allows for disabled config
    """

    sflow_sensors = []
    netflow_sensors = []

    def __init__(self, sensors, pmacct):
        ports = set()
        unique_identifiers = set()
        for key in sensors:
            o = SensorObjet(key)
            if o.enabled is False:
                continue
            if o.port in ports:
                raise Exception(
                    "invalid configuration.  Port {} is already used with a different configuration".format(
                        o.port
                    )
                )
            key = (o.name, o.instance)
            if key in unique_identifiers:
                raise Exception(
                    "Invalid Configuration.  All enabled sensors must have a unique sensorID + InstanceID combination"
                )
            valid = False
            if o.type == "sflow":
                self.sflow_sensors.append(o)
                o.image = pmacct.image("sflow")
                valid = True
            else:
                self.netflow_sensors.append(o)
                o.image = pmacct.image("netflow")
                valid = True

            if valid:
                ports.add(o.port)
                unique_identifiers.add(key)


class PmfAcctConfig(object):
    def __init__(self, data, rabbit):
        self.accepted_types = ["netflow", "sflow"]
        self.__config__ = copy(data)
        self.__rabbit__ = rabbit

    @property
    def rabbit(self):
        return self.__rabbit__

    def is_valid(self, requested_type):
        return requested_type in self.accepted_types

    def config_type(self, requested_type):
        if self.is_valid(requested_type):
            return self.__config__.get(requested_type, {}).get("pmacctd_type")

    @property
    def types(self):
        return self.accepted_types

    def image(self, requested_type):
        if self.is_valid(requested_type):
            return self.__config__.get(requested_type, {}).get("image")

    @property
    def netflow_config(self):
        return self.__config__.get("netflow", {})

    @property
    def sflow_config(self):
        return self.__config__.get("sflow", {})


class RabbitConfig(object):
    def __init__(self, data) -> None:
        super().__init__()
        print("Hello")
        if data is None or len(data) == 0:
            raise Exception("Invalid configuration.  Missing MessageQueue config")
        self.__data__ = copy(data)

    def get_dict(self) -> dict:
        return copy(self.__data__)

    ##@property
    def hostname(self) -> str:
        return self.__data__.get("rabbitmq_host")

    @property
    def user(self) -> str:
        return self.__data__.get("rabbitmq_user")

    @property
    def password(self) -> str:
        return self.__data__.get("rabbitmq_host")

    def __str__(self) -> str:
        print("it was called now")
        return "rabbitStr"


class Config(object):
    __instance__ = None
    __config__ = {}
    __pmfconfig__ = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @property
    def dev_generate(self):
        return gila.get("include_dev_generate")

    @property
    def dev_queue(self):
        return gila.get("include_dev_queue")

    @property
    def environment(self):
        return gila.get("environment_file")

    @property
    def deploy_path(self):
        return gila.get("deployment_location")

    @property
    def template_folder(self):
        return gila.get("template_folder")

    def template_path(self, template_type, file):
        return os.path.join(
            self.template_folder,
            gila.get("template_locations.{}".format(template_type)),
            file,
        )

    @property
    def sensors(self):
        return self.__sensors__

    @property
    def pmacct_config(self):
        return self.__pmfconfig__

    @classmethod
    def load_config(cls):
        gila.set_default("paths.template_dir", "./conf/")
        gila.set_default("paths.template_dir", "templates")

    @classmethod
    def instance(cls, debug=False, config_path="./conf", config_file="app.yaml"):
        if cls.__instance__ is None:
            logger.debug("Creating new configuration instance")
            cls.__instance__ = cls.__new__(cls)

            cls.load_config()

            gila.set_config_name(config_file)
            gila.automatic_env()
            gila.add_config_path(config_path)
            gila.read_config_file()

            # allow CLI override
            if debug:
                gila.override("debug", debug)
            cls.__config__ = gila.all_config()

            rabbit_dict = gila.all_config().get("mq_config", {})
            rabbit_config = RabbitConfig(rabbit_dict)
            cls.__pmfconfig__ = PmfAcctConfig(
                cls.__config__.get("pmacct", {}), rabbit_config
            )
            cls.__sensors__ = SensorConfig(
                cls.__config__.get("sensors", {}), cls.__pmfconfig__
            )

        return cls.__instance__
