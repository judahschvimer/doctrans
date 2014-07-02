from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "veri"}
app.config["SECRET_KEY"] = "KeepThisS3cr3t"
from app import views

db = MongoEngine(app)

if __name__ == '__main__':
    app.run()

