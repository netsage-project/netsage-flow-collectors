from gen_lib.config import Config, PmfAcctConfig, load_config
from gen_lib.sensors import SensorObjet
import gila
import pytest


@pytest.fixture()
def config():
    load_config("./gen_config/collectors.template.yml", False)
    config = Config.instance()
    yield config


class TestPmfAcctConfig:
    # def test_that_depends_on_resource(self, resource):
    def test_types(self, config):
        resource = config.__pmfconfig__
        assert resource.is_valid("netflow") is True
        assert resource.is_valid("sflow") is True
        assert resource.is_valid("error") is False
        assert resource.image("netflow") == "pmacct/nfacctd:v1.7.5"
        assert resource.image("sflow") == "pmacct/sfacctd:v1.7.5"


class TestConfig:
    def test_config(self, config):
        assert config.deploy_path == "deploy"
        assert config.dev_generate is False
        assert config.dev_queue is False
        assert config.environment == "env.example"
        assert config.template_folder == "templates"
        assert config.sensors is not None
        assert config.pmacct_config is not None

    def test_sensors(self, config):
        data = gila.all_config()
        sensorData = data["sensors"][0]
        sensorData['instanceID'] = 'foobar'
        failed = False
        try:
            SensorObjet(sensorData)
        except Exception as e:
            failed = True
            assert str(e) == 'InstanceID \'foobar\' needs to be numeric'

        assert failed is True
