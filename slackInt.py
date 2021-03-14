import datetime
import logging
import math
import os

from slack import WebClient as SlackClient

from github import GithubWebhookPayloadParser
from github import getRecipientGithubUserNameByAction
from github import lookupGithubFullName


def notifyRecipient(data):
    print(data)
    payload = createSlackMessagePayload(data)
    sendSlackMessage(payload)


def createSlackMessagePayload(data):
    pr_metadata = getPullRequestMetadata(data)

    msg_text = getMessage(pr_metadata, data)
    message = buildPayload(msg_text, pr_metadata)

    return message


def getMessage(pr_metadata, data):
    if data.get('action') == 'review_requested':
        actionMessage = 'asked by {author} to review a pull request'.format(author=pr_metadata.get('author'))
    elif data.get('action') == 'assigned':
        actionMessage = 'assigned a pull request by {author}'.format(author=pr_metadata.get('author'))
    else:
        actionMessage = 'pinged'

    msg_text = "You've been {action}. Lucky you!".format(action=actionMessage)
    if pr_metadata.get('channel') == os.environ.get('DEFAULT_NOTIFICATION_CHANNEL'):
        github_username = getUnmatchedUserName(data)
        msg_text = '{}! {}'.format(github_username, msg_text)

    return msg_text


def buildPayload(msg_text, pr_metadata):
    message = {
        "text": msg_text,
        "as_user": True,
        "link_names": True,
        "channel": pr_metadata.get('channel'),
        "attachments": [
            {
                "fallback": "<{}|{}>".format(pr_metadata.get('url'), pr_metadata.get('title')),
                "color": "#36a64f",
                "author_name": "{} pull request #{}".format(pr_metadata.get('repo'), pr_metadata.get('number')),
                "author_link": pr_metadata.get('url'),
                "author_icon": "https://github.com/favicon.ico",
                "title": pr_metadata.get('title'),
                "title_link": pr_metadata.get('url'),
                "text": pr_metadata.get('description'),
                "footer": "Github PR Notifier",
                "footer_icon": pr_metadata.get('author_image'),
                "ts": int(datetime.datetime.now().timestamp())
            }
        ]
    }
    return message


def getPullRequestMetadata(data):
    print(data)
    pullRequestData = {}
    payloadParser = GithubWebhookPayloadParser(data)

    pullRequestData['url'] = payloadParser.getPullRequestUrl()
    pullRequestData['title'] = payloadParser.getPullRequestTitle() or 'Unknown Title'
    pullRequestData['repo'] = payloadParser.getPullRequestRepo() or 'Unknown'
    pullRequestData['number'] = payloadParser.getPullRequestNumber() or math.pi
    pullRequestData['author_image'] = payloadParser.getPullRequestAuthorImage()
    pullRequestData['description'] = payloadParser.getPullRequestDescription()
    pullRequestData['channel'] = getNotificationChannel(data)

    pullRequestAuthor = getSlackUserNameByGithubUserName(payloadParser.getPullRequestAuthor())

    if pullRequestAuthor:
        pullRequestAuthor = '@{}'.format(pullRequestAuthor)
    else:
        pullRequestAuthor = 'someone'

    pullRequestData['author'] = pullRequestAuthor

    return pullRequestData


def getNotificationChannel(data):
    github_username = getRecipientGithubUserNameByAction(data)
    slack_username = getSlackUserNameByGithubUserName(github_username)

    if slack_username:
        channel = '@{}'.format(slack_username)
    else:
        channel = os.environ.get('DEFAULT_NOTIFICATION_CHANNEL')

    return channel


def getSlackUserNameByGithubUserName(github_username):  # pylint: disable=invalid-name
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    response = slack_client.api_call("users.list")
    users = response.get('members', [])

    if github_username:
        slack_username = matchSlackGithubUserName(users, github_username)
        if not slack_username:
            full_name = lookupGithubFullName(github_username)
            slack_username = matchSlackUserNameByFullName(users, full_name)
        return slack_username
    return None


def matchSlackGithubUserName(users, github_username):
    for user in users:
        if isinstance(user, dict) and (
                user.get('name').lower() == github_username.lower()
                or user.get('profile', {}).get('display_name', '').lower() == github_username.lower()
        ):
            return user.get('name')
    return None


def matchSlackUserNameByFullName(users, full_name):
    if full_name:
        for user in users:
            if isinstance(user, dict) and user.get('real_name', '').strip().lower() == full_name.strip().lower():
                return user.get('name')
    return None


def getUnmatchedUserName(data):
    payloadParser = GithubWebhookPayloadParser(data)
    github_username = payloadParser.get_request_reviewer_username()

    if github_username is not None:
        return '@{}'.format(github_username)

    return 'Hey you, tech people'


def sendSlackMessage(payload):
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    response = slack_client.api_call(api_method = "chat.postMessage", json = payload)

    logger = logging.getLogger(__name__)
    if not response.get('ok'):
        logger.warning('Unable to send message. Response: %s\nPayload:\n%s', response, payload)
    else:
        logger.info('Success!')
