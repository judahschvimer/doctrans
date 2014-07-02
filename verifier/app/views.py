from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
import models
from . import app
import json
from bson import json_util

@app.route('/')
@app.route('/index')
def index():
    t=models.get_sentence()
    return json.dumps(t, default=json_util.default)
#json.loads(aJsonString, object_hook=json_util.object_hook) to deserialize

@app.route('/add', methods = ['POST'])
def post_translation():
    print request.get_json()
    t = models.Translation()
    res=t.ingest(request.get_json())
    if not res: 
        print t.state   
        t.save()
        
        return "Success" 
    else:
        return "Failed"

