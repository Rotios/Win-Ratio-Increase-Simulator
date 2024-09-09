import json

import simulator

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': json.dumps({'message': str(err)}) if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    try:
        print("Received event: " + json.dumps(event, indent=2))

        operations = ['POST']

        operation = event['httpMethod']
        if operation in operations:
            payload = json.loads(event['body'])
            return respond(None, simulator.handle_event(payload))
        else:
            raise ValueError('Unsupported method "{}"'.format(operation))
    except ValueError as e:
        return respond(e)