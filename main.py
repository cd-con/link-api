from flask import Flask, request, jsonify

import datetime
import json

import settings

app = Flask(__name__)


def read_api_info():
    with open(settings.api_info_file, "r") as info_file:
        return json.loads(info_file.readline())


api_data = read_api_info()

link_queue = []
data_queue = []


@app.route(f'/api/{api_data["version"]["id"]}/')
def index():
    server_time = round(datetime.datetime.timestamp(datetime.datetime.now()))
    return jsonify({"code": 200, "content": {}, "debug": {"text": f"API ready. Server datetime: "
                                                                  f"{server_time}\n"
                                                                  f"API authors: "
                                                                  f"{''.join(api_data['version']['authors'])}\n"
                                                                  f"API released: "
                                                                  f"{api_data['version']['date']}"}})


@app.route(f'/api/{api_data["version"]["id"]}/link/create')
def create_link_request():
    uid = request.args.get("uid")  # very very long string
    key = request.args.get("key")  # 6-digit code
    if uid is None or key is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "UID and Key must not be equal to None"}},
                        "debug": {}})
    for link in link_queue:
        if link["uid"] == uid:
            return jsonify({"code": 200, "content": {"error": {"title": "Link already in queue",
                                                               "description": ""}},
                            "debug": {}})

    link_queue.append({"uid": uid, "paired_uid": None, "key": key, "paired": False})
    return jsonify({"code": 200, "content": {},
                    "debug": {"text": "Link created!"}})


@app.route(f'/api/{api_data["version"]["id"]}/link/pair')
def response_link_request():
    uid = request.args.get("uid")
    key = request.args.get("key")  # 6-digit code
    if uid is None or key is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "Key must not be equal to None"}},
                        "debug": {}})
    for link in link_queue:
        if link["key"] == key and not link["paired"]:
            link["paired"] = True
            link["paired_uid"] = uid
            return jsonify({"code": 200, "content": {"uid": link["uid"]},
                            "debug": {"text": f"Paired with {link['uid']}"}})

    return jsonify({"code": 200, "content": {"error": {"title": "Link does not exsist",
                                                       "description": ""}},
                    "debug": {}})


@app.route(f'/api/{api_data["version"]["id"]}/link')
def check_linking():
    uid = request.args.get("uid")  # 6-digit code
    if uid is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "UID must not be equal to None"}},
                        "debug": {}})
    for link in link_queue:
        if link["uid"] == uid and link["paired"]:
            link_queue.remove(link)
            return jsonify({"code": 200, "content": {"uid": link["paired_uid"]},
                            "debug": {"text": f"Paired with {link['paired_uid']}"}})
        elif link["uid"] == uid:
            return jsonify({"code": 200, "content": {},
                            "debug": {"text": "Waiting for pairing"}})
    return jsonify({"code": 200, "content": {"error": {"title": "Pairing error",
                                                       "description": "Link does not exsist"}},
                    "debug": {}})


@app.route(f'/api/{api_data["version"]["id"]}/link/remove')
def remove_linking():
    pass


@app.route(f'/api/{api_data["version"]["id"]}/link/send')
def send():
    uid = request.args.get("uid")  # 6-digit code
    data = request.args.get("data")  # 6-digit code
    if uid is None or data is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "UID and Data must not be equal to None"}},
                        "debug": {}})
    data_queue.append({"uid": uid, "data": data})
    return jsonify({"code": 200, "content": {},
                    "debug": {"text": "Data sended."}})


@app.route(f'/api/{api_data["version"]["id"]}/link/get')
def get():
    uid = request.args.get("uid")  # 6-digit code
    if uid is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "UID must not be equal to None"}},
                        "debug": {}})
    for data in data_queue:
        if data["uid"] == uid:
            data_queue.remove(data)
            return jsonify({"code": 200, "content": {"data": data["data"]},
                            "debug": {}})
    return jsonify({"code": 200, "content": {},
                    "debug": {"text": "No new data avaliable"}})


if __name__ == '__main__':
    app.run()
