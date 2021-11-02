import json
import os
import s3_dao

def handler(event, context):
    s3_cache_bucket_name = os.getenv('DATA_BUCKET')
    s3_cache_file_name = os.getenv('CACHE_FILE_NAME')
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': s3_dao.download_report(s3_cache_bucket_name, s3_cache_file_name)
    }
