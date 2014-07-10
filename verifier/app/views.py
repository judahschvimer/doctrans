from flask import  request, redirect, render_template, url_for
from flask.views import MethodView
import models
from . import app
import json
from bson import json_util
import logging
import urllib

logger = logging.getLogger('views')
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
@app.route('/index')
def language_picker():
    languages = models.get_languages()
    return render_template("language_picker.html", language_list=languages)

@app.route('/<language>')
def file_browser(language):
    files = models.get_file_names('en', language)
    return render_template("file_browser.html",file_list=files, language=language)

@app.route('/<language>/<file>')
def file_editor(file, language):
    sentences = models.get_sentences_in_file(urllib.url2pathname(file), 'en', language)    
    return render_template('file_editor.html', sentence_list=sentences, language=language)

@app.route('/add', methods=['POST'])
def edit_translation():
    try:
        j = fix_json(request.json)
        logger.debug(j)
        t = models.Sentence(j[u'old'][u'_id'])

        if t.status is "approved":
            return json.dumps({ "code": 404 , "msg": "Can't edit approved sentence" }), 404

        t.edit(j[u'new'][u'editor'], j[u'new'][u'new_target_sentence']) 
        return json.dumps({ "code": 200 , "msg": "Edit Succeeded" }), 200 
    except KeyError:
        return json.dumps({ "code": 404 , "msg": "Edit Failed" }), 404

@app.route('/approve', methods=['POST'])
def approve_translation():
    j = fix_json(request.json)
    t = models.Sentence(j[u'old'][u'_id'])
    approver = models.User(j[u'new'][u'approver'])
    if approver._id is userID:
        return json.dumps({ "code": 404 , "msg": "Can't approve own edit" }), 404
    prev_editor = models.User(t.userID)
    try:
        t.approve(prev_editor, approver)
        return json.dumps({ "code:":200, "msg":"Approval Succeeded"}),200 
    except:
        return json.dumps({ "code:":200, "msg":"Can't approve same sentence twice"}),200 
        

@app.route('/unapprove', methods=['POST'])
def unapprove_translation():
    j = fix_json(request.json)
    t = models.Sentence(j[u'old'])
    unapprover = models.User(j[u'new'][u'unapprover'])
    prev_editor = models.User(t.userID)
    t.unapprove(prev_editor, unapprover)
    return json.dumps({ "code:":200, "msg":"Unapproval Succeeded"}),200 

def fix_json(json_object):
    return json.loads(json.dumps(json_object, default=json_util.default), object_hook=json_util.object_hook)
