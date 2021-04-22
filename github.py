import copy
import os

import requests
from werkzeug.exceptions import BadRequest


def isValidPullRequest(data):
    isValidRequest = validatePullRequest(data)
    isValidAction = data.get('action') == 'review_requested' or data.get('action') == 'assigned'

    return isValidRequest and isValidAction


def validatePullRequest(data):
    if 'action' not in data:
        raise BadRequest('no event supplied')

    if 'pull_request' not in data or 'html_url' not in data.get('pull_request'):
        raise BadRequest('payload.pull_request.html_url missing')

    return True


def getRecipientGithubUserNameByAction(data):
    payloadParser = GithubWebhookPayloadParser(data)

    if data.get('action') == 'review_requested':
        username = payloadParser.getRequestReviewerUserName()
    elif data.get('action') == 'assigned':
        username = payloadParser.getAssigneeUserName()
    else:
        raise BadRequest('Github username not found')

    return username


def lookupGithubFullName(gh_username):
    url = 'https://api.github.com/users/{}'.format(gh_username)
    request = requests.get(url, auth=(os.environ.get('GITHUB_API_USER', ''), os.environ.get('GITHUB_API_TOKEN', '')))
    user = request.json()
    return user.get('name', '')


def checkReviewResponse(data):
    pass


class GithubWebhookPayloadParser:
    """ A class to parse a github payload and return specific elements. """

    def __init__(self, data=None):
        if data is None:
            data = {}
        self._data = copy.deepcopy(data)

    def getRequestReviewerUserName(self):
        """ Parse and retrieve the requested reviewer username. """
        return self._data.get('requested_reviewer', {}).get('login')

    def getAssigneeUserName(self):
        """ Parse and retrieve the assignee's username. """
        return self._data.get('assignee', {}).get('login')

    def getPullRequestTitle(self):
        """ Parse and retrieve the pull request title. """
        return self._data.get('pull_request', {}).get('title')

    def getPullRequestUrl(self):
        """ Parse and retrieve the pull request html url. """
        return self._data.get('pull_request', {}).get('html_url')

    def getPullRequestRepo(self):
        """ Parse and retrieve the pull request repository name. """
        return self._data.get('repository', {}).get('full_name')

    def getPullRequestNumber(self):
        """ Parse and retrieve the pull request number. """
        return self._data.get('number')

    def getPullRequestAuthor(self):
        """ Parse and retrieve the pull request author. """
        return self._data.get('pull_request', {}).get('user', {}).get('login')

    def getPullRequestAuthorImage(self):
        """ Parse and retrieve the pull request author image. """
        return self._data.get('pull_request', {}).get('user', {}).get('avatar_url')

    def getPullRequestDescription(self):
        """ Parse and retrieve the pull request repository description. """
        return self._data.get('pull_request', {}).get('body')
