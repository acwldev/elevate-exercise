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
    s3_cache_bucket_name = os.getenv('DATA_BUCKET')
    s3_cache_file_name = os.getenv('CACHE_FILE_NAME')

    report = create_report(secret_credentials_arn)
    data_uploader.upload_report(s3_cache_bucket_name, s3_cache_file_name, str(report))

def create_report(secret_credentials_arn):
    secrets = boto3.client('secretsmanager')
    credentials = secrets.get_secret_value(SecretId=secret_credentials_arn)['SecretString'].split(',')
    username = credentials[0]
    password = credentials[1]
    identity_mapping = data_puller.get_identity_mapping(IDENTITIES_FQDN, username, password)
    audit_profiles_by_type_and_id = {}
    all_ids = set()
    for incident_type in INCIDENT_TYPES:
        destination_url = INCIDENTS_FQDN + incident_type
        raw_data = data_puller.get_audit_data(destination_url, username, password)
        audit_profiles_by_id = data_transformer.transform_raw_data(raw_data, incident_type, identity_mapping)
        all_ids.update(audit_profiles_by_id.keys())
        audit_profiles_by_type_and_id[incident_type] = audit_profiles_by_id
    return data_transformer.aggregate_data(all_ids, audit_profiles_by_type_and_id)
