import boto3
import os
from zipfile import ZipFile
import json

def lambda_handler(event, context):
    
    s3 = boto3.resource('s3')
    stepfunction = boto3.client('stepfunctions')

    try:
        src_bucket = event['Records'][0]['s3']['bucket']['name']
        src_key = event['Records'][0]['s3']['object']['key']
        filename = os.path.basename(src_key)
        table_name = os.path.splitext(filename)[0]
        target_bucket = '<YourDatalakeBucket>'
        files_list = []

        s3.meta.client.download_file(src_bucket, src_key, f'/tmp/{filename}')
        
        with ZipFile(f'/tmp/{filename}', 'r') as zipObj:
            zipObj.extractall('/tmp/unzipped')
        
        
        for file in os.listdir('/tmp/unzipped'):
            s3.meta.client.upload_file(f'/tmp/unzipped/{file}', target_bucket, f'raw/{table_name}/{file}')
            files_list.append(file)
            
        stepfunction.start_execution(
            stateMachineArn='arn:aws:states:us-east-2:<AccountID>:stateMachine:convert-crawl-data',
            input=json.dumps({"table" : table_name})
        )
        
    except Exception as e:
        s3.meta.client.copy({'Bucket': src_bucket, 'Key': src_key}, src_bucket, f'out/{filename}')
    finally:
        s3.Object(src_bucket, src_key).delete()
    
    return files_list
