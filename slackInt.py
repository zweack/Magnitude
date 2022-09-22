"""Generate salck message and send it to appropriate recipient."""

import datetime
import logging
import math
import os

from slack import WebClient as SlackClient

from github import GithubWebhookPayloadParser
from github import getRecipientGithubUserNameByAction
from github import lookupGithubFullName


def notifyRecipient(data):
    """Notify the selected recipient on slack."""
    payload = createSlackMessagePayload(data)
    sendSlackMessage(payload)


def createSlackMessagePayload(data):
    """Create payload for slack notification."""
    pr_metadata = getPullRequestMetadata(data)

    msgText = getMessage(prMetadata, data)
    message = buildPayload(msgText, prMetadata)

    return message


def getMessage(pr_metadata, data):
    """Generate message based on github action."""
    if data.get('action') == 'review_requested':
        actionMessage = 'asked by {author} to review a pull request'.format(
            author=pr_metadata.get('author'))
    elif data.get('action') == 'assigned':
        actionMessage = 'assigned a pull request by {author}'.format(
            author=pr_metadata.get('author'))
    else:
        actionMessage = 'pinged'

    msgText = "You've been {action}. Good luck!".format(action=actionMessage)
    if prMetadata.get('channel') == os.environ.get('DEFAULT_NOTIFICATION_CHANNEL'):
        github_username = getUnmatchedUserName(data)
        msgText = '{}! {}'.format(github_username, msgText)

    return msgText


def buildPayload(msg_text, pr_metadata):
    """Build slack notification payload from github action data."""
    message = {
        "text": msgText,
        "as_user": True,
        "link_names": True,
        "channel": prMetadata.get('channel'),
        "attachments": [
            {
                "fallback": "<{}|{}>".format(prMetadata.get('url'), prMetadata.get('title')),
                "color": "#36a64f",
                "author_name": "{} pull request #{}".format(prMetadata.get('repo'), prMetadata.get('number')),
                "author_link": prMetadata.get('url'),
                "author_icon": "https://github.com/favicon.ico",
                "title": prMetadata.get('title'),
                "title_link": prMetadata.get('url'),
                "text": prMetadata.get('description'),
                "footer": "PR Notifications by Magnitude",
                "footer_icon": prMetadata.get('author_image'),
                "ts": int(datetime.datetime.now().timestamp())
            }
        ]
    }
    return message


def getPullRequestMetadata(data):
    """Fetch pull request metadata."""
    pullRequestData = {}
    payloadParser = GithubWebhookPayloadParser(data)

    pullRequestData['url'] = payloadParser.getPullRequestUrl()
    pullRequestData['title'] = payloadParser.getPullRequestTitle(
    ) or 'Unknown Title'
    pullRequestData['repo'] = payloadParser.getPullRequestRepo() or 'Unknown'
    pullRequestData['number'] = payloadParser.getPullRequestNumber() or math.pi
    pullRequestData['author_image'] = payloadParser.getPullRequestAuthorImage()
    pullRequestData['description'] = payloadParser.getPullRequestDescription()
    pullRequestData['channel'] = getNotificationChannel(data)

    pullRequestAuthor = getSlackUserNameByGithubUserName(
        payloadParser.getPullRequestAuthor())

    if pullRequestAuthor:
        pullRequestAuthor = '@{}'.format(pullRequestAuthor)
    else:
        pullRequestAuthor = 'someone'

    pullRequestData['author'] = pullRequestAuthor

    return pullRequestData


def getNotificationChannel(data):
    """Get target slack channel for notification."""
    github_username = getRecipientGithubUserNameByAction(data)
    slack_username = getSlackUserNameByGithubUserName(github_username)
    if slack_username:
        channel = '@{}'.format(slack_username)
    else:
        channel = os.environ.get('DEFAULT_NOTIFICATION_CHANNEL')

    return channel


def getSlackUserNameByGithubUserName(github_username):
    """Get slack username based on github username."""
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
    """Compare slack and github username for a user."""
    for user in users:
        if isinstance(user, dict) and (
                user.get('name').lower() == github_username.lower()
                or user.get('profile', {}).get('display_name', '').lower() == github_username.lower()
        ):
            return user.get('name')
    return None


def matchSlackUserNameByFullName(users, full_name):
    """Compare salck username with github user full name."""
    if full_name:
        for user in users:
            if isinstance(user, dict) and user.get('real_name', '').strip().lower() == full_name.strip().lower():
                return user.get('name')
    return None


def getUnmatchedUserName(data):
    """Set username for unmatched user in slack."""
    payloadParser = GithubWebhookPayloadParser(data)
    github_username = payloadParser.getRequestReviewerUserName()

    if github_username is not None:
        return '@{}'.format(github_username)

    return 'Hey you, tech people'


def sendSlackMessage(payload):
    """Send generated slack message ."""
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    response = slack_client.api_call(
        api_method="chat.postMessage", json=payload)

    logger = logging.getLogger(__name__)
    if not response.get('ok'):
        logger.warning(
            'Unable to send message. Response: %s\nPayload:\n%s', response, payload)
    else:
        logger.info('Success!')
