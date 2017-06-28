import config
import tests.test_credentials
from pxvm.libs.proxlib import Prox


def test_version():
    px = Prox(config.PX_HOST, user=tests.test_credentials.autotest_user, password=tests.test_credentials.autotest_pw)
    response = px.get_version()
    assert 'version' in response
