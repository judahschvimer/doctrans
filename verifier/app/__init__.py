from flask import Flask
from flask.ext.mongoengine import MongoEngine
import config

app = Flask(__name__)
app.config.from_object(config)

from app import views
from app import filters

db = MongoEngine(app)

if __name__ == '__main__':
    app.run()

