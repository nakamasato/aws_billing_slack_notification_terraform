import os
import boto3
import json
import requests
from datetime import datetime
from datetime import date

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
MIN_COST = 0.01


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

    return sorted(
        [
            {
                'service_name': item['Keys'][0],
                'billing': float(item['Metrics']['AmortizedCost']['Amount'])
            }
            for item 
            in response['ResultsByTime'][0]['Groups']
        ], 
        key=lambda k: k['billing'],
        reverse=True
    )


def get_message(total_billing, service_billings):
    start = datetime.strptime(total_billing['start'], '%Y-%m-%d').strftime('%m/%d')
    end = datetime.strptime(total_billing['end'], '%Y-%m-%d').strftime('%m/%d')
    total = round(float(total_billing['billing']), 2)

    title = f'{start}～{end} total: {total:.2f} USD'

    filtered_billings = [
        item for item
        in service_billings 
        if item['billing'] > MIN_COST
    ]
    rows = [
        '- %s: %.2f USD' % 
        (
            item['service_name'], 
            float(item['billing'])
        )
        for item 
        in filtered_billings
    ]
    return title, '\n'.join(rows)


def post_slack(title, detail):

    payload = {
        'attachments': [
            {
                'color': 'good',
                'pretext': title,
                'text': detail
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        print(response.status_code)


def get_begin_of_month():
    today = date.today()
    return date(today.year, today.month, 1).isoformat()


def get_today():
    return date.today().isoformat()
