from flask import  request, redirect, render_template, url_for
from flask.views import MethodView
import models
from . import app
import json
from bson import json_util
import logging
import urllib
import traceback

logger = logging.getLogger('views')
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
@app.route('/index')
def language_picker():
    ''' This view shows the valid languages '''
    languages = models.get_languages()
    return render_template("language_picker.html", language_list=languages)

@app.route('/file/<username>/<language>')
def file_browser(language, username):
    ''' This view shows the valid files
    :Parameters:
        - 'language': the current target language
        - 'username': the current user
    '''
    files = models.get_file_names('en', language)
    return render_template("file_browser.html",file_list=files, language=language, username=username)

@app.route('/file/<username>/<language>/<path:file>')
def file_editor(file, language, username):
    ''' This view shows the sentences in a file to edit
    :Parameters:
        - 'file': the file currently being edited
        - 'language': the current target language
        - 'username': the current user
    '''
    sentences = models.get_sentences_in_file(urllib.url2pathname(file), 'en', language)    
    return render_template('file_editor.html', sentence_list=sentences, language=language, username=username)

@app.route('/add', methods=['POST'])
def edit_translation():
    ''' This function is called when a user posts an edit.
    It first validates the edit and then it it submits it to the database
    '''
    try:
        j = fix_json(request.json)
        logger.debug(j)
        t = models.Sentence(oid=j[u'old'][u'_id'])

        if t.status is "approved":
            return json.dumps({ "code": 404 , "msg": "Can't edit approved sentence" }), 404

        editor = models.User(username=j[u'new'][u'editor'])
        t.edit(editor, j[u'new'][u'new_target_sentence']) 
        return json.dumps({ "code": 200 , "msg": "Edit Succeeded" }), 200 
    except KeyError:
        return json.dumps({ "code": 401 , "msg": "Edit Failed" }), 404
    except Exception:
        return json.dumps({ "code": 402 , "msg": "Edit Failed" }), 404
        
@app.route('/approve', methods=['POST'])
def approve_translation():
    ''' This function is called when a user approves a sentence.
    It first validates the approval and then it it submits it to the database
    '''
    j = fix_json(request.json)
    t = models.Sentence(oid=j[u'old'][u'_id'])
    approver = models.User(username=j[u'new'][u'approver'])
    prev_editor = models.User(oid=t.userID)
    try:
        t.approve(prev_editor, approver)
        return json.dumps({ "code:":200, "msg":"Approval Succeeded"}),200 
    except Exception as e:
        logger.error(traceback.format_exc())
        return json.dumps({ "code:":405, "msg":"Approval Failed"}),405
        

@app.route('/unapprove', methods=['POST'])
def unapprove_translation():
    ''' This function is called when a user posts an edit.
    It first validates the edit and then it it submits it to the database
    '''
    j = fix_json(request.json)
    t = models.Sentence(oid=j[u'old'][u'_id'])
    unapprover = models.User(username=j[u'new'][u'unapprover'])
    prev_editor = models.User(oid=t.userID)
    try:
        t.unapprove(prev_editor, unapprover)
        return json.dumps({ "code:":200, "msg":"Unapproval Succeeded"}),200 
    except Exception:
        return json.dumps({ "code:":406, "msg":"Unapproval Failed"}),200 
        

def fix_json(json_object):
    ''' helper function to fix json from request for mongodb
    :Parameters:
    - 'json_object': some json object
    :Returns:
    - a better json object
    '''
    return json.loads(json.dumps(json_object, default=json_util.default), object_hook=json_util.object_hook)
