import boto3

def upload_report(s3_bucket_name, s3_cache_file, report):
    s3_client = boto3.resource('s3')
    s3_client.Object(s3_bucket_name, s3_cache_file).put(Body=report)
