# Magnitude
#### Get automated Github Pull Requests notification for individual team members or on your team's channel on Slack

#### Pull Request Assigned
![assigned](https://github.com/zweack/Magnitude/blob/dev/static/pr_assigned.png)
#### Pull Request Review Requested
![review_requested](https://github.com/zweack/Magnitude/blob/dev/static/review_requested.png)

### Target Audience
This application is developed for corporate employees who may not be able to configure Github-Slack integration due restrictions behind corporate networks.

### Application Setup
1. Create a [Github Personal Access Token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) which will be used to lookup github username/full name.
2. Create a [Slack Application](https://api.slack.com/apps?new_app=1&ref=bolt_start_hub) which will be used to configure Slack Bot.
3. Create a [Slack Bot](https://slack.com/intl/en-gb/help/articles/115005265703-Create-a-bot-for-your-workspace#create-a-bot) using the application created in previous step. Give appropriate read and write scopes to your bot.
4. Clone this repo and deploy it on a dedicated server in your corporate network/cloud. For demo purpose, I have deployed this on [Heroku](https://dashboard.heroku.com/apps). Make sure that `app.py` is configured as starting point of the application on your host. 
5. Create a custom [Github Webhook](https://docs.github.com/en/developers/webhooks-and-events/creating-webhooks) in a repo whose Pull Request notifications you want to trigger. <br/> If host address is `abc.com`, put webhook URL as `abc.com/hooks` <br/> Put a strong webhook secret and make a note of it.
6. Configure a new/existing channel to be used as default in case a username is not resolved. Add your Slack Bot in this channel. 
7. Setup following Environment Variables on your server:

   ```
   SLACK_BOT_TOKEN=[YOUR SLACKBOT TOKEN] 
   GITHUB_API_TOKEN=[YOUR GITHUB API TOKEN]
   GITHUB_API_USER=[YOUR GITHUB USERNAME]
   GITHUB_WEBHOOKS_KEY=[YOUR GITHUB WEBHOOK SECRET]
   DEFAULT_NOTIFICATION_CHANNEL=[YOUR DEFAULT SLACK CHANNEL]
   ```
8. Thats it. Now create a pull request, assign it to yourself or request review from someone and see the notification triggered on your Slack.

Work In Progress: To send notification when a pull request is reviewed and approved or change(s) requested.
