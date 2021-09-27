import os
import sys
from tokenize import String

#reuse libs directory
current_dir = os.path.dirname(os.path.abspath(__file__))
libs = "/".join(
    current_dir.split('/')[0:-1]
)

sys.path.append(libs)
from flask import flash, redirect, request, jsonify
from flask import (
    Flask,
    render_template,
    url_for
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    BooleanField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
)
from flask_mongoengine import MongoEngine, Document
#from flask_mongoengine.wtf import model_form, model_fields
#from wtforms.ext.
from mongoengine import connect
from mongoengine.context_managers import no_dereference
#from gpiozero import *
from RPi import GPIO
import json
import requests
import re
from pymongo import ReadPreference
from pylibs.schema.user_schemas import System, Relay, Pin
from pylibs.forms.pi_server import RelayForm

SECRET_KEY = os.urandom(32)







app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = {
    'host': '127.0.0.1',
    'port': 27017,
    'db': 'static'
}

app.config['SECRET_KEY'] = SECRET_KEY
db = MongoEngine(app)


conn = connect(db='static')
#print(conn)

#print(Pin.objects().count())

# try:
#     for pin in Pin.objects:
#         print(pin.to_json())
# except StopIteration as stop_iteration_error:
#     print('generation done')
# except RuntimeError as runtime_error:
#     print('generation done')


@app.route('/api/test', methods=['GET'])
def api_test():
    return jsonify({
        "status": "200",
        "message": "success"
    })

@app.route('/api/system', methods=['POST', 'GET', 'DELETE'])
def api_system():
    #print()
    args = request.args
    results = []

    if request.json is not None and len(args.keys()) == 0:
        print("json input in request data, using as search filder")
        search_data = request.json
        print(f"search_data: {search_data}")
        try:
            for system in System.objects(**search_data):
                print(system.model)
                results.append(json.loads(system.to_json()))
        except RuntimeError as runtime_error:
            print('results done..')
        finally:
            return jsonify(results)
    elif request.json is None and len(args.keys()) == 0:
        print("should render a template here..")
        try:
            for system in System.objects():
                print(system.model)
                results.append(json.loads(system.to_json()))
        except RuntimeError as runtime_error:
            print('results done..')
        finally:
            return render_template('system.html', system=results[0])
    else:
        if 'json_output' in args and bool(args['json_output']):
            print('json output set via args')
            try:
                for system in System.objects():
                    print(system.model)
                    results.append(json.loads(system.to_json()))
            except RuntimeError as runtime_error:
                print('results done..')
            finally:
                return jsonify(results)
        else:
            print('json output set via args')
            try:
                for system in System.objects():
                    print(system.model)
                    results.append(json.loads(system.to_json()))
            except RuntimeError as runtime_error:
                print('results done..')
            finally:
                return jsonify(results)


@app.route('/api/gpios', methods=['POST','GET','DELETE'])
def api_gpio():
    args = request.args
    results = []
    print(args)
    #sending json data - receiving json outputs
    if request.json is not None and len(args.keys()) == 0:
        search_data = request.json
        print(f"search_data: {search_data}")
        try:
            for pin in Pin.objects(**search_data):
                print(pin.label)
                print(pin.data.descr)
                #print(json.dumps(search_data))
                #print(json.loads(pin.to_json()))
                results.append(json.loads(pin.to_json()))
        except RuntimeError as runtime_error:
            print('results  done..')
        finally:
            return jsonify(results)
    elif request.json is None and 'json_output' in args and bool(args['json_output']):
        try:
            for pin in Pin.objects():
                print(pin.label)
                print(pin.data.descr)
                results.append(json.loads(pin.to_json()))
        except RuntimeError as runtime_error:
            print('results  done..')
        finally:
            #return jsonify(results)
            return jsonify(results)
    else:
        try:
            for pin in Pin.objects():
                print(pin.label)
                print(pin.data.descr)
                results.append(json.loads(pin.to_json()))
        except RuntimeError as runtime_error:
            print('results  done..')
        finally:
            #return jsonify(results)
            return render_template("pin.html", results=results)


@app.route('/api/relays', methods=['GET','POST','DELETE'])
def api_relays():
    results = []
    json_data = request.json
    args = request.args
    form = RelayForm()
    results = []
    try:
        for relay in Relay.objects:
            results.append(json.loads(relay.to_json()))
    except RuntimeError as runtime_error:
        print('results done..')
    if request.method == 'GET':
        print('processed get')
        if json_data is None and 'json_output' in args and bool(args['json_output']):
            print('json_outputs...')
            print(json_data)
            print(args)
            try:
                for relay in Relay.objects:
                    results.append(json.loads(relay.to_json()))
            except RuntimeError as runtime_error:
                return jsonify(results)
        else:
            print('form outputs...')
            if form.validate_on_submit():
                return render_template("relay.html", form=form, results=results)
    elif request.method == 'DELETE':
        print('processed delete')
        try:
            for relay in Relay.objects:
                print(dir(relay.to_json()))
                #print(dir(relays.objects))
                relay.delete()
        except RuntimeError as runtime_error:
            jsonify({'deleted': True})
    elif request.method == 'POST':
        print('processed post')
        args_len = len(list(args.keys()))
        if form.is_submitted() and json_data is None and args_len == 0:
            #print(f"JSON_DATA is: {json_data}")
            flash(
                dict(
                    description=form.description.data,
                    relay_channel=form.relay_channel.data,
                    board_port=form.board_port.data,
                    gpio_port=form.gpio_port.data,
                    normally_open=form.normally_open.data,
                ))

            relay = Relay(**dict(
                description=str(form.description.data),
                relay_channel=int(form.relay_channel.data),
                board_port=int(form.board_port.data),
                gpio_port=int(form.gpio_port.data),
                normally_open=bool(form.normally_open.data),
            ))
            relay.save()
            render_template("relay.html", form=form, results=results)
            #return render_template("replay.html", form=form, results=results)

        elif (json_data is None and args_len > 0) and not form.is_submitted():
            flash(f"JSON_DATA is: {json_data}")

            relay = Relay(
                dict(
                    description=str(args.get('description')),
                    relay_channel=int(args.get('relay_channel')),
                    board_port=int(args.get('board_port')),
                    gpio_port=int(args.get('gpio_port')),
                    normally_open=bool(args.get('normally_open')),
                ))
            relay.save()
            return render_template("relay.html", form=form, results=results)
        elif (json_data is not None and args_len == 0) and not form.is_submitted():
            obj = json.dumps(json_data)
            flash(f"JSON_DATA is: {json_data}")
            return jsonify({'json_data': True})
    return render_template("relay.html", form=form, results=results)


app.run(
    host='0.0.0.0',
    port=5001
)

#Pin()
#print(os.path.abspath(__file__))
