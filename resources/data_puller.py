import boto3
import urllib.parse
import urllib.request
import urllib.response

BASE_FQDN = 'https://incident-api.use1stag.elevatesecurity.io/incidents/'
INCIDENT_TYPES = [
    'denial',
    'intrusion',
    'executable',
    'misuse',
    'unauthorized',
    'probing',
    'other'
]

def getAuditData(secretCredentialsArn):
    secrets = boto3.client('secretsmanager')
    credentials = secrets.get_secret_value(SecretId=secretCredentialsArn)['SecretString'].split(',')
    username = credentials[0]
    password = credentials[1]
    for incident_type in INCIDENT_TYPES:
        destination_url = BASE_FQDN + incident_type

        p = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, destination_url, username, password)
        auth_handler = urllib.request.HTTPBasicAuthHandler(p)
        opener = urllib.request.build_opener(auth_handler)
        urllib.request.install_opener(opener)

        try:
            result = opener.open(destination_url)
            messages = result.read()
            return messages
        except IOError as e:
            print (e)
