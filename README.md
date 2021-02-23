# ![Sereno logo](static/img/logo_long.png) for Slack



[![Build Status](https://travis-ci.com/serenoapp/slackbot.svg?token=ypsRxux3KfFXBbsBkLEM&branch=main)](https://travis-ci.com/serenoapp/slackbot)

Sereno is an open source ChatOps that can be integrated with Slack to help and assist you during an incident.
Sereno needs to be deployed in AWS Lambda and it uses DynamoDB

You can also directly install Sereno for Slack in your workspace

[<img alt="Add to Slack" height="35" width="129" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x">](https://slack.com/oauth/v2/authorize?scope=incoming-webhook,app_mentions:read,channels:history,chat:write,commands&client_id=1129483761414.1582197345009&redirect_uri=https://api.sereno.app/slack/auth)


### Features
* Integrates with Zoom and Jira (more to come!) freeing engineers from having to deal with the common steps needed during the start of an incident
* Creates an incident slack channel whenever a new incident is opened 
* Logs in a Jira ticket the activity happening in the incident channel to help with postmortems
* Saves a contact as oncall. The oncall will be automatically added to the incident channel
* Notifies people that have been set as responders and adds them to the incident channel.


### Run Slackbot locally
1 - Install python dependencies 
* `pip install -r requirements.txt`

2 - Install dynamodb local
* Install the plugin: `sls dynamodb install`
* Start dynamodb local instance: `sls dynamodb start`

3 - Run the script to populate the database tables with needed data (here you'll need to replace the values expecting tokens)
* `sh populate-dynamodb-table.sh` (script is located in the root directory)

4 - In a different terminal run ngrok in port 5000
* `./ngrok http 5000` (you have to install ngrok separately)

5 - Run serverless server locally
* `sls wsgi serve`

You should be able to start using `@Sereno` slackbot!

### Deploy to AWS
Slackbot uses Serverless framework. All you need to do is 
`sls deploy`
### Test

Test has been written using standar pytest, so just run `pytest` from command line.

### About us
Sereno Slackbot is part of an Incident Management platform called, yes, you guessed it right, Sereno.
You can check out our platform here https://sereno.app