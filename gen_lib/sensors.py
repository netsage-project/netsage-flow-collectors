from copy import copy


class SensorObjet(object):
    def __init__(self, data):
        self.__data__ = copy(data)

    @property
    def image(self):
        """
        Docker image name.
        """
        return self.__data__.get("image")

    @image.setter
    def image(self, value):
        self.__data__["image"] = value

    @property
    def enabled(self):
        """
        Denotes if the sensor is enabled or not
        """
        return self.__data__.get("enabled", True)

    @property
    def type(self):
        """
        returns netflow or sflow as appropriate
        """
        return self.__data__.get("type")

    @property
    def port(self):
        """
        port the collector (pmacct) is listening on.
        """
        return self.__data__.get("port")

    @property
    def name(self):
        """
        The name of the sensor that uniquely identifies it in our data collection
        """
        return self.__data__.get("sensorName")

    @property
    def instance(self):
        """
        instance name if hostname should be overrideen.
        """
        return self.__data__.get("instanceName")
