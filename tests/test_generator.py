
import config

from pxvm.libs.proxlib import Prox


def test_version():
    px = Prox(config.PX_HOST, user='autotest@pve', password='autotest')
    response = px.get_version()
    assert 'version' in response
