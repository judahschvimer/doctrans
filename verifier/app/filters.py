from . import app
import json
from bson import json_util
import urllib

def to_json(value):
    return json.dumps(value, default=json_util.default)

def pathname2url(path):
    return urllib.pathname2url(path)

app.jinja_env.filters['to_json'] = to_json
app.jinja_env.filters['pathname2url'] = pathname2url
