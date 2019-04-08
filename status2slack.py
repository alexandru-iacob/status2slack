#!/usr/bin/env python

import os
import sys
import json
import requests
from requests.exceptions import ConnectionError

# in AWS Lambda, use:
# SLACK_WEBHOOK = os.environ["SLACK_WEBHOOK"]
SLACK_WEBHOOK = "https://hooks.slack.com/services/xxxxxxxxxxxxxxxxxxxxxxxx"
SLACK_MSG_TYPE_OK = "green"
SLACK_MSG_TYPE_NOK = "red"

SENDGRID_STATUS_DATA = "https://3tgl2vf85cht.statuspage.io/api/v2/summary.json"
SENDGRID_STATUS = "http://status.sendgrid.com/"
MARKETO_STATUS_DATA = "https://67fdp51vjkft.statuspage.io/api/v2/summary.json"
MARKETO_STATUS = "https://status.marketo.com/"
MIXPANEL_STATUS_DATA = "https://x4m91ldrf511.statuspage.io/api/v2/summary.json"
MIXPANEL_STATUS = "https://status.mixpanel.com/"
INTERCOM_STATUS_DATA = "https://1m1j8k4rtldg.statuspage.io/api/v2/summary.json"
INTERCOM_STATUS = "https://www.intercomstatus.com/"

def get_status(provider_status_url, provider_name = None):
    SEND_SLACK_UPDATE_OK = False
    SEND_SLACK_UPDATE_NOK = False

    # LOCAL FILE TESTS
    #with open("/home/alexi/Downloads/summary-incident.json", "r") as stream:
    #    JSON_DATA = json.load(stream)
    # END LOCAL FILE TEST

    r = requests.get(provider_status_url)
    JSON_DATA = r.json()
    GLOBAL_CURRENT_STATUS = JSON_DATA['status']['description']
    LAST_UPDATE = JSON_DATA['page']['updated_at']

    if provider_name == "Sendgrid":
        provider_url = SENDGRID_STATUS
    elif provider_name == "Marketo":
        provider_url = MARKETO_STATUS
    elif provider_name == "Mixpanel":
        provider_url = MIXPANEL_STATUS
    elif provider_name == "Intercom":
        provider_url = INTERCOM_STATUS

    INCIDENTS_COUNT = len(JSON_DATA['incidents'])
    if INCIDENTS_COUNT > 0:
        for INCIDENT in JSON_DATA['incidents']:

            # check all updates related to the incident
            INCIDENT_UPDATES = len(INCIDENT['incident_updates'])
            for UPDATE in INCIDENT['incident_updates']:
                COMPONENTS_AFFECTED = len(UPDATE['affected_components'])
                if COMPONENTS_AFFECTED > 0:
                    for COMPONENT in UPDATE['affected_components']:
                        INCIDENT_COMPONENT = INCIDENT['name'] + ' - ' + COMPONENT['name']
                        if COMPONENT['old_status'] == COMPONENT['new_status']:
                            SEND_SLACK_UPDATE_OK = False
                            print
                            print "---------------------------------------------"
                            print "No status updates. Delaying Slack updates ..."
                            print "---------------------------------------------"
                            print
                        elif COMPONENT['new_status'] == "operational":
                            SEND_SLACK_UPDATE_OK = True
                            slack_msg(SLACK_MSG_TYPE_OK, provider_name, provider_url, INCIDENT['name'], COMPONENT['new_status'])
                        else:
                            SEND_SLACK_UPDATE_NOK = True
                if SEND_SLACK_UPDATE_NOK:
                    slack_msg(SLACK_MSG_TYPE_NOK, provider_name, provider_url, INCIDENT_COMPONENT, COMPONENT['new_status'] ,COMPONENT['new_status'], UPDATE['created_at'], UPDATE['updated_at'])
                elif SEND_SLACK_UPDATE_OK:
                    slack_msg(SLACK_MSG_TYPE_OK, provider_name, provider_url, INCIDENT_COMPONENT, INCIDENT['status'])


    # don't spam the channel if everything is OK
    if GLOBAL_CURRENT_STATUS == "All Systems Operational":
        print
        print("----------------- {} - {} --------------------").format(provider_name, GLOBAL_CURRENT_STATUS)

def slack_msg(type, provider, url, incident_name = None, status = None, incident_status = None, incident_created = None, incident_updated = None):

    incident_data = {
        "attachments": [
            {
                "fallback": "Update status2slack",
                "color": "#ff4500",
                "pretext": "{} status update".format(provider.upper()),
                "author_name": "Update",
                "title": "{}".format(incident_name),
                "title_link": "{}".format(url),
                "text": "Created: {}".format(incident_created),
                "fields": [
                   {
                      "title": "{}".format(status),
                      "value": "Updated: {}".format(incident_updated),
                      "short": "false"
                   }
                ]
            }
        ]
    }
    data = {
        "attachments": [
            {
                "fallback": "Update status2slack",
                "color": "#008000",
                "pretext": "Update status2slack notification",
                "author_name": "Update",
                "title": "Status update for {}".format(provider.upper()),
                "title_link": "{}".format(url),
                "text": "{} - {}".format(incident_name, status)
            }
        ]
    }

    if type == "green":
        slack_msg = data
    else:
        slack_msg = incident_data

    print
    print("^^^^^^^^^^^^^^^^ STATUS UPDATED ({})^^^^^^^^^^^^^^^^^^^^^^^^^").format(type)
    print("Provider - {}").format(provider)
    print("URL: {}").format(url)
    print("Incident: {}").format(incident_name)
    print("Status: {}").format(status)
    if incident_created or incident_updated is not None:
        print("Incident created: {}").format(incident_created)
        print("Incident updated: {}").format(incident_updated)
    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    print

    send_slack_msg(slack_msg)

def send_slack_msg(data):
    response = requests.post(SLACK_WEBHOOK, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    print('Response: ' + str(response.text))
    print('Response code: ' + str(response.status_code))

def main():
    get_status(SENDGRID_STATUS_DATA, "Sendgrid")
    get_status(MARKETO_STATUS_DATA, "Marketo")
    get_status(MIXPANEL_STATUS_DATA, "Mixpanel")
    get_status(INTERCOM_STATUS_DATA, "Intercom")

if __name__ == "__main__":
        main()

