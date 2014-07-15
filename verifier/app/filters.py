from flask_app import app
import json
from bson import json_util
import urllib
import models

def to_json(value):
    ''' This filter converts value to json
    :Parameters:
        - 'value': string to convert to json
    :Returns:
        - The json version of the string
    '''
    return json.dumps(value, default=json_util.default)

def pathname2url(path):
    ''' This filter convert a path to a file to a url
    :Parameters:
        - 'path': path to a file
    :Returns:
        - The string of the path
    '''
    return urllib.pathname2url(path)

def check_if_user_approved(user, sentenceID):
    ''' This filter checks if the user approved the sentence
    :Parameters:
        - 'user': the user
        - 'sentenceID': the sentence
    :Returns:
        - a boolean saying if the user approved the sentence 
    '''
    s=models.Sentence(oid=sentenceID)
    return models.User(username=user)._id in s.state['approvers']

def check_if_user_edited(user, sentenceID):
    ''' This filter checks if the user edited the sentence
    :Parameters:
        - 'user': the user
        - 'sentenceID': the sentence
    :Returns:
        - a boolean saying if the user edited the sentence 
    '''
    s=models.Sentence(oid=sentenceID)
    return models.User(username=user)._id == s.state['userID']

def get_userID(user):
    ''' This filter gets userID ofa  user
    :Parameters:
        - 'user': the user
    :Returns:
        - userID
    '''
    return models.User(username=user)._id


app.jinja_env.filters['to_json'] = to_json
app.jinja_env.filters['pathname2url'] = pathname2url
app.jinja_env.filters['check_if_user_approved'] = check_if_user_approved
app.jinja_env.filters['check_if_user_edited'] = check_if_user_edited
app.jinja_env.filters['get_userID'] = get_userID
