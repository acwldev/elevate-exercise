import boto3
import data_puller
import data_transformer
import data_uploader
import json
import os
import urllib.parse
import urllib.request
import urllib.response

IDENTITIES_FQDN = 'https://incident-api.use1stag.elevatesecurity.io/identities/'
INCIDENTS_FQDN = 'https://incident-api.use1stag.elevatesecurity.io/incidents/'
INCIDENT_TYPES = [
    'denial',
    'intrusion',
    'executable',
    'misuse',
    'unauthorized',
    'probing',
    'other'
]

def handler(event, context):
    secret_credentials_arn = os.getenv('CREDENTIALS_ARN')
    s3_cache_bucketname = os.getenv('DATA_BUCKET')
    report = create_report(secret_credentials_arn)
    data_uploader.upload_report(s3_cache_bucketname, report)

def create_report(secret_credentials_arn):
    secrets = boto3.client('secretsmanager')
    credentials = secrets.get_secret_value(SecretId=secret_credentials_arn)['SecretString'].split(',')
    username = credentials[0]
    password = credentials[1]
    identity_mapping = data_puller.get_identity_mapping(IDENTITIES_FQDN, username, password)
    all_transformed_data = {}
    for incident_type in INCIDENT_TYPES:
        destination_url = INCIDENTS_FQDN + incident_type
        raw_data = data_puller.get_audit_data(destination_url, username, password)
        all_transformed_data[incident_type] = data_transformer.transform_raw_data(raw_data, incident_type, identity_mapping)
    return data_transformer.aggreagate_data(all_transformed_data)
