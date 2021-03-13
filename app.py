import os
from flask import Flask
from flask_hookserver import Hooks

app = Flask(__name__)
app.config['GITHUB_WEBHOOKS_KEY'] = os.environ.get('GITHUB_WEBHOOKS_KEY')
app.config['VALIDATE_IP'] = (os.environ.get('GIT_HOOK_VALIDATE_IP', 'True').lower() not in ['false', '0'])
app.config['VALIDATE_SIGNATURE'] = (os.environ.get('GIT_HOOK_VALIDATE_SIGNATURE', 'True').lower() not in ['false', '0'])

hooks = Hooks(app, url='/hooks')

@hooks.hook('ping')
def ping(data, guid):
	return 'pong'

@app.route("/")
def index():
	return "Welcome!"


app.run()