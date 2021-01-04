from gen_lib.config import Config, PmfAcctConfig, load_config
import pytest

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
        assert config.dev_generate is True
        assert config.dev_queue is True
        assert config.environment == "env.example"
        assert config.template_folder == "templates"
        assert config.sensors is not None
        assert config.pmacct_config is not None
