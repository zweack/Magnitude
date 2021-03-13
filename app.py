import os
from flask import Flask
from flask_hookserver import Hooks

from github import isValidPullRequest
from slack import notifyRecipient

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
	return "<h1>Will update this page soon !!</h1>"


@HOOKS.hook('pull_request')
def pull_request(data, guid):
    if isValidPullRequest(data):
        notifyRecipient(data)
        result = 'Recipient Notified'
    else:
        result = 'Action ({}) ignored'.format(data.get('action'))

    return result


if __name__ == '__main__':
	app.run(threaded=True, port=5000)