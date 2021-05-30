"""
Entry point of the appliction
"""

import os
from flask import Flask
from flask_hookserver import Hooks

from github import isValidPullRequest
from slackInt import notifyRecipient

app = Flask(__name__)
app.config['GITHUB_WEBHOOKS_KEY'] = os.environ.get('GITHUB_WEBHOOKS_KEY')
app.config['VALIDATE_IP'] = False
app.config['VALIDATE_SIGNATURE'] = False

hooks = Hooks(app, url='/hooks')


@hooks.hook('ping')
def ping():
    """Test Function."""
    return 'pong'


@app.route("/")
def index():
    """Print sample HTML (converted from readme)"""
    return """
    <!DOCTYPE html><html><head><meta charset="utf-8"><title>Magnitude</title><style>body {
    font-family: "Lucida Console", "Courier New", monospace;}</style></head><body id="preview">
    <h1 class="code-line" data-line-start=0 data-line-end=1><a id="Magnitude_0"></a>Magnitude</h1>
    <h4 class="code-line" data-line-start=1 data-line-end=2><a id="Get_automated_Github_Pull_Requests_notification_for_individual_team_members_or_on_your_teams_channel_on_Slack_1"></a>Get automated Github Pull Requests notification for individual team members or on your team’s channel on Slack</h4>
    <h4 class="code-line" data-line-start=3 data-line-end=4><a id="Pull_Request_Assigned_3"></a>Pull Request Assigned</h4>
    <p class="has-line-data" data-line-start="4" data-line-end="5"><img src="https://raw.githubusercontent.com/zweack/Magnitude/dev/static/pr_assigned.png" alt="assigned"></p>
    <h4 class="code-line" data-line-start=5 data-line-end=6><a id="Pull_Request_Review_Requested_5"></a>Pull Request Review Requested</h4>
    <p class="has-line-data" data-line-start="6" data-line-end="7"><img src="https://raw.githubusercontent.com/zweack/Magnitude/dev/static/review_requested.png" alt="review_requested"></p>
    <h3 class="code-line" data-line-start=8 data-line-end=9><a id="Target_Audience_8"></a>Target Audience</h3>
    <p class="has-line-data" data-line-start="9" data-line-end="10">This application is developed for corporate employees who may not be able to configure Github-Slack integration due restrictions behind corporate networks.</p>
    <h3 class="code-line" data-line-start=11 data-line-end=12><a id="Application_Setup_11"></a>Application Setup</h3>
    <ol>
    <li class="has-line-data" data-line-start="12" data-line-end="13">
    <p class="has-line-data" data-line-start="12" data-line-end="13">Create a <a href="https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/">Github Personal Access Token</a> which will be used to lookup github username/full name.</p>
    </li>
    <li class="has-line-data" data-line-start="13" data-line-end="14">
    <p class="has-line-data" data-line-start="13" data-line-end="14">Create a <a href="https://api.slack.com/apps?new_app=1&amp;ref=bolt_start_hub">Slack Application</a> which will be used to configure Slack Bot.</p>
    </li>
    <li class="has-line-data" data-line-start="14" data-line-end="15">
    <p class="has-line-data" data-line-start="14" data-line-end="15">Create a <a href="https://slack.com/intl/en-gb/help/articles/115005265703-Create-a-bot-for-your-workspace#create-a-bot">Slack Bot</a> using the application created in previous step. Give appropriate read and write scopes to your bot.</p>
    </li>
    <li class="has-line-data" data-line-start="15" data-line-end="16">
    <p class="has-line-data" data-line-start="15" data-line-end="16">Clone this repo and deploy it on a dedicated server in your corporate network/cloud. For demo purpose, I have deployed this on <a href="https://dashboard.heroku.com/apps">Heroku</a>. Make sure that <code>app.py</code> is configured as starting point of the application on your host.</p>
    </li>
    <li class="has-line-data" data-line-start="16" data-line-end="17">
    <p class="has-line-data" data-line-start="16" data-line-end="17">Create a custom <a href="https://docs.github.com/en/developers/webhooks-and-events/creating-webhooks">Github Webhook</a> in a repo whose Pull Request notifications you want to trigger. &lt;br/&gt; If host address is <code>abc.com</code>, put webhook URL as <code>abc.com/hooks</code> &lt;br/&gt; Put a strong webhook secret and make a note of it.</p>
    </li>
    <li class="has-line-data" data-line-start="17" data-line-end="18">
    <p class="has-line-data" data-line-start="17" data-line-end="18">Configure a new/existing channel to be used as default in case a username is not resolved. Add your Slack Bot in this channel.</p>
    </li>
    <li class="has-line-data" data-line-start="18" data-line-end="27">
    <p class="has-line-data" data-line-start="18" data-line-end="19">Setup following Environment Variables on your server:</p>
    <pre><code class="has-line-data" data-line-start="21" data-line-end="27">SLACK_BOT_TOKEN=[YOUR SLACKBOT TOKEN] 
    GITHUB_API_TOKEN=[YOUR GITHUB API TOKEN]
    GITHUB_API_USER=[YOUR GITHUB USERNAME]
    GITHUB_WEBHOOKS_KEY=[YOUR GITHUB WEBHOOK SECRET]
    DEFAULT_NOTIFICATION_CHANNEL=[YOUR DEFAULT SLACK CHANNEL]
    </code></pre>
    </li>
    <li class="has-line-data" data-line-start="27" data-line-end="29">
    <p class="has-line-data" data-line-start="27" data-line-end="28">Thats it. Now create a pull request, assign it to yourself or request review from someone and see the notification triggered on your Slack.</p>
    </li>
    </ol>
    <p class="has-line-data" data-line-start="29" data-line-end="30">Work In Progress: To send notification when a pull request is reviewed and approved or change(s) requested.</p>
    </body></html>
    """


@hooks.hook('pull_request')
def pull_request(data, guid):
    """Verify pull request data and send slack notification."""
    if isValidPullRequest(data):
        notifyRecipient(data)
        result = 'Recipient Notified'
    else:
        result = 'Action ({}) ignored'.format(data.get('action'))

    return result


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
