from gen_lib.config import PmfAcctConfig
import pytest

import pytest

@pytest.fixture()
def resource():
    res = PmfAcctConfig(**{})
    yield res

class TestPmfAcctConfig:
    # def test_that_depends_on_resource(self, resource):
    def test_types(self, resource):
        assert resource.is_valid("netflow") is True
        assert resource.is_valid("sflow") is True
        assert resource.is_valid("error") is False
