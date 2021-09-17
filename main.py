from flask import Flask, request, jsonify

import datetime
import json

import settings

app = Flask(__name__)

link_queue = []
data_queue = []


def read_api_info():
    with open(settings.api_info_file, "r") as info_file:
        return json.loads(info_file.readline())

'''
Get API data
'''
api_data = read_api_info()


@app.route(f'/api/{api_data["version"]["id"]}/')
def index():
    '''
    Landing page. For debug use only.
    
    Returns server and API info.
    '''
    server_time = round(datetime.datetime.timestamp(datetime.datetime.now()))
    return jsonify({"code": 200, "content": {}, "debug": {"text": f"API ready. Server datetime: "
                                                                  f"{server_time}\n"
                                                                  f"API authors: "
                                                                  f"{''.join(api_data['version']['authors'])}\n"
                                                                  f"API released: "
                                                                  f"{api_data['version']['date']}"}})


@app.route(f'/api/{api_data["version"]["id"]}/link/create')
def create_link_request():
    '''
    Register link in queue
    '''
    
    uid = request.args.get("uid")  # very very long string
    key = request.args.get("key")  # X-digit code
    if uid is None or key is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "UID and Key shouldn't be equal to 0"}},
                        "debug": {}})
    for link in link_queue:
        if link["uid"] == uid:
            return jsonify({"code": 200, "content": {"error": {"title": "Link already in queue",
                                                               "description": "-"}},
                            "debug": {}})

    link_queue.append({"uid": uid, "paired_uid": None, "key": key, "paired": False})
    
    return jsonify({"code": 200, "content": {},
                    "debug": {"text": "Link created!"}})


@app.route(f'/api/{api_data["version"]["id"]}/link/pair')
def response_link_request():
    '''
    Connect using link
    '''
    uid = request.args.get("uid")  # very very long string
    key = request.args.get("key")  # 6-digit code
    
    if uid is None or key is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "Key shouldn't be equal to None"}},
                        "debug": {}})
    
    for link in link_queue:
        if link["key"] == key and not link["paired"]:
            link["paired"] = True
            link["paired_uid"] = uid
            return jsonify({"code": 200, "content": {"uid": link["uid"]},
                            "debug": {"text": f"Paired with {link['uid']}"}})

    return jsonify({"code": 200, "content": {"error": {"title": "Link does not exsist",
                                                       "description": "-"}},
                    "debug": {}})


@app.route(f'/api/{api_data["version"]["id"]}/link')
def check_linking():
    '''
    Check linking status.
    '''   
    
    uid = request.args.get("uid")  # very very long string
    
    if uid is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "UID shouldn't be equal to None"}},
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
                                                       "description": "Linking does not exsist"}},
                    "debug": {}})


@app.route(f'/api/{api_data["version"]["id"]}/link/remove')
def remove_linking():
    '''
    Indev.
    '''
    pass


@app.route(f'/api/{api_data["version"]["id"]}/link/send')
def send():
    '''
    Put data in data queue.
    
    Looks like I'm created another UDP protocol :)

    TO-DO: make some kind of verification
    '''
    uid = request.args.get("uid")  # very very long string
    data = request.args.get("data")  # content
    if uid is None or data is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "UID and Data shouldn't be equal to None"}},
                        "debug": {}})
    data_queue.append({"uid": uid, "data": data})
    return jsonify({"code": 200, "content": {},
                    "debug": {"text": "Data sended."}})


@app.route(f'/api/{api_data["version"]["id"]}/link/get')
def get():
    '''
    Get data from data queue
    '''
    uid = request.args.get("uid")  # very very long string
    if uid is None:
        return jsonify({"code": 200, "content": {"error": {"title": "Input error",
                                                           "description": "UID shouldn't be equal to None"}},
                        "debug": {}})
    for data in data_queue:
        if data["uid"] == uid:
            data_queue.remove(data)
            return jsonify({"code": 200, "content": {"data": data["data"]},
                            "debug": {}})
    return jsonify({"code": 200, "content": {},
                    "debug": {"text": "No new data"}})


if __name__ == '__main__':
    app.run()  # Let's goooo
