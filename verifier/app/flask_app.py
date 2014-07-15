from flask import Flask
from flask.ext.mongoengine import MongoEngine
import config

app = Flask(__name__)
app.config.from_object(config)

db = MongoEngine(app)
