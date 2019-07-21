import os
import boto3
import json
import requests
from datetime import datetime
from datetime import date

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']


def lambda_handler(event, context):
    client = boto3.client('ce', region_name='us-east-1')

    total_billing = get_total_billing(client)
    service_billings = get_service_billings(client)

    (title, detail) = get_message(total_billing, service_billings)
    post_slack(title, detail)
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "successfully sent to slack"
            }
        )
    }


def get_total_billing(client):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': get_begin_of_month(),
            'End': get_today()
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost'
        ]
    )
    return {
        'start': response['ResultsByTime'][0]['TimePeriod']['Start'],
        'end': response['ResultsByTime'][0]['TimePeriod']['End'],
        'billing': response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount'],
    }


def get_service_billings(client):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': get_begin_of_month(),
            'End': get_today()
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost'
        ],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    billings = []

    for item in response['ResultsByTime'][0]['Groups']:
        billings.append({
            'service_name': item['Keys'][0],
            'billing': item['Metrics']['AmortizedCost']['Amount']
        })
    return billings


def get_message(total_billing, service_billings):
    start = datetime.strptime(total_billing['start'], '%Y-%m-%d').strftime('%m/%d')
    end = datetime.strptime(total_billing['end'], '%Y-%m-%d').strftime('%m/%d')
    total = round(float(total_billing['billing']), 2)

    title = f'{start}～{end} total: {total:.2f} USD'

    details = []
    for item in service_billings:
        service_name = item['service_name']
        billing = round(float(item['billing']), 2)

        if billing == 0.0:
            continue
        details.append(f'　・{service_name}: {billing:.2f} USD')

    return title, '\n'.join(details)


def post_slack(title, detail):
    # https://api.slack.com/incoming-webhooks
    # https://api.slack.com/docs/message-formatting
    # https://api.slack.com/docs/messages/builder
    payload = {
        'attachments': [
            {
                'color': '#36a64f',
                'pretext': title,
                'text': detail
            }
        ]
    }

    # http://requests-docs-ja.readthedocs.io/en/latest/user/quickstart/
    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        print(response.status_code)


def get_begin_of_month():
    today = date.today()

    # ISO 8601
    return date(today.year, today.month, 1).isoformat()


def get_today():
    # ISO 8601
    return date.today().isoformat()
