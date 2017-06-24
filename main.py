import os
import config
from flask import Flask, request, json
from pxvm.libs.proxlib import Prox

app = Flask(__name__)


def _make_response(data):
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/api/version", methods=['GET'])
def version():
    try:
        user, password = request.headers.get('Authorization').split(':')
    except (ValueError, AttributeError):
        return 'Please send Authorization header ([user]@pam:[password])'
    px = Prox(config.PX_HOST, user=user, password=password)
    return _make_response(px.get_version())


@app.route("/api/nodes", methods=['GET'])
def nodes():
    try:
        user, password = request.headers.get('Authorization').split(':')
    except (ValueError, AttributeError):
        return 'Please send Authorization header ([user]@pam:[password])'
    px = Prox(config.PX_HOST, user=user, password=password)
    return _make_response(px.get_nodes())


@app.route("/api/lxc", methods=['GET', 'POST'])
def lxc():
    try:
        user, password = request.headers.get('Authorization').split(':')
    except (ValueError, AttributeError):
        return 'Please send Authorization header ([user]@pam:[password])'
    px = Prox(config.PX_HOST, user=user, password=password)
    if request.method == 'POST':
        return _make_response(px.create_lxc(ostemplate=config.DEFAULT_TEMPLATE, ip=config.DEFAULT_IP,
                                            gw=config.DEFAULT_GW, ssh=config.SSH_KEYS))
    if request.method == 'GET':
        return _make_response(px.get_vms())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT'))