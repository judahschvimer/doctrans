from . import app
import json
from bson import json_util
import urllib
import models

def to_json(value):
    return json.dumps(value, default=json_util.default)

def pathname2url(path):
    return urllib.pathname2url(path)

def check_if_user_approved(user, sentenceID):
    s=models.Sentence(oid=sentenceID)
    return models.User(username=user)._id in s.state['approvers']

def check_if_user_edited(user, sentenceID):
    s=models.Sentence(oid=sentenceID)
    return models.User(username=user)._id == s.state['userID']

def get_userID(user):
    return models.User(username=user)._id


app.jinja_env.filters['to_json'] = to_json
app.jinja_env.filters['pathname2url'] = pathname2url
app.jinja_env.filters['check_if_user_approved'] = check_if_user_approved
app.jinja_env.filters['check_if_user_edited'] = check_if_user_edited
app.jinja_env.filters['get_userID'] = get_userID
