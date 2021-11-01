import json
import data_puller
import os

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': data_puller.getAuditData(
                    secretCredentialsArn = os.getenv('CREDENTIALS_ARN')
                )
    }
