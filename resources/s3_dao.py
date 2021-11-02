import boto3

def upload_report(bucket_name, file_path, report):
    s3_client = boto3.resource('s3')
    s3_client.Object(bucket_name, file_path).put(Body=report)

def download_report(bucket_name, file_path):
    s3_client = boto3.resource('s3')
    obj = s3_client.Object(bucket_name, file_path)
    return obj.get()['Body'].read().decode('utf-8')
