import boto3
import json
import urllib.parse
import urllib.request
import urllib.response

def get_cached_report(bucket_name):
    pass

def get_identity_mapping(destination_url, username, password):
    return get_data(destination_url, username, password)

def get_audit_data(destination_url, username, password):
    return get_data(destination_url, username, password)['results']

def get_data(destination_url, username, password):
    p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    p.add_password(None, destination_url, username, password)
    auth_handler = urllib.request.HTTPBasicAuthHandler(p)
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)
    try:
        result = opener.open(destination_url)
        return json.loads(messages)
    except IOError as e:
        return P{}
        print (e)
