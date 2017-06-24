import os
from flask import Flask, request, json
from libs.proxlib import Prox

app = Flask(__name__)

PX_HOST = 'pve.home.tekoone.ru'
DEFAULT_TEMPLATE = 'local:vztmpl/ubuntu-16.04-standard_16.04-1_amd64.tar.gz'
DEFAULT_GW = '10.160.18.1'
DEFAULT_IP = '10.160.18.{}/24'
SSH_KEYS = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCtbCa4zzsFlQgPmghFLR0FPEwD0XUKWdsQ9UZCVTLBNMtOxkd77aqeLT/f29ICGMnf' \
           'MDV6SfFaxN/uWJukQ0onPTNHTQwyJsxGZdrKBByhS0jBp4SXfoU6KH1gA/m8CykC0WSBzdJRT/1RemYAuC+AzklLthEO/F8gnC97QAWm' \
           'ix7govUrJWFQZ9k8pgybB3YUFu3SSqt/Q5PGfxFW8jmkpxFWi6DrBa4Yfuu7oP7d0p4+nYHbhTRPO0E1sXzZPBijXaVOzFJybgB/pYhX' \
           '8JcpBrVPd3LffVIPfeFiC8b4dk3cX3ITkuzDQn423BzEOfrnlHj2R+WouvXKaHFM+bld root@delta\n'


def _make_response(data):
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/api/lxc", methods=['GET', 'POST'])
def lxc():
    try:
        user, password = request.headers.get('Authorization').split(':')
    except (ValueError, AttributeError):
        return 'Please send Authorization header ([user]@pam:[password])'
    px = Prox(PX_HOST, user=user, password=password)
    if request.method == 'POST':
        return _make_response(px.create_lxc(ostemplate=DEFAULT_TEMPLATE, ip=DEFAULT_IP, gw=DEFAULT_GW, ssh=SSH_KEYS))
    if request.method == 'GET':
        return _make_response(px.get_vms())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT'))