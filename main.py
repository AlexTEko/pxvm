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


def _request():
    try:
        user, password = request.headers.get('Authorization').split(':')
    except (ValueError, AttributeError) as e:
        return e
    return Prox(config.PX_HOST, user=user, password=password)


@app.route("/api/version", methods=['GET'])
def version():
    return _make_response(_request().get_version())


@app.route("/api/nodes", methods=['GET'])
def nodes():
    return _make_response(_request().get_nodes())


@app.route("/api/tasks", methods=['GET'])
def tasks():
    return _make_response(_request().get_tasks())

@app.route("/api/tasks/<int:vmid>", methods=['GET'])
def task(vmid):
    return _make_response(_request().get_tasks(vmid))


@app.route("/api/lxc", methods=['GET', 'POST'])
def lxc():
    if request.method == 'POST':
        return _make_response(_request().create_lxc(ostemplate=config.DEFAULT_TEMPLATE, ip=config.DEFAULT_IP,
                                            gw=config.DEFAULT_GW, ssh=config.SSH_KEYS))
    if request.method == 'GET':
        return _make_response(_request().get_vms())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT'), threaded=True)