import os
from flask import Flask
from flask_hookserver import Hooks

app = Flask(__name__)
app.config['GITHUB_WEBHOOKS_KEY'] = os.environ.get('GITHUB_WEBHOOKS_KEY')
app.config['VALIDATE_IP'] = False
app.config['VALIDATE_SIGNATURE'] = False

hooks = Hooks(app, url='/hooks')

@hooks.hook('ping')
def ping(data, guid):
	return 'pong'

@app.route("/")
def index():
	return "<h1>Welcome to our server !!</h1>"


if __name__ == '__main__':
	app.run(threaded=True, port=5000)