from copy import copy


class SensorObjet(object):
    def __init__(self, data):
        self.__data__ = copy(data)

    @property
    def enabled(self):
        return self.__data__.get("enabled", True)

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
