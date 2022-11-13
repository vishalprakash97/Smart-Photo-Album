import json
import os
import time
import logging
import boto3
import requests
from datetime import datetime

credentials = (os.environ["username"],os.environ["password"])
host_url = os.environ["host_url"]
index_name = 'photos'
type_name = 'Photo'
region = 'us-east-1' 
service = 'es'

def lambda_handler(event, context):
    # TODO implement
    print("Photo Added")
    #print(event)
    
    bucket_name=event["Records"][0]["s3"]['bucket']['name']
    file_name=event["Records"][0]["s3"]['object']['key']
    print(bucket_name)
    print(file_name)
    client = boto3.client("rekognition")
    response = client.detect_labels(Image={"S3Object": {
        "Bucket": bucket_name, "Name": file_name}}, MaxLabels=10, MinConfidence=70)
    labels=[]   
    for label in response['Labels']:
        print (label['Name'] + ' : ' + str(label['Confidence']))
        labels.append(label['Name'].lower())
    
    print("going into metadata")
    #####
    s3_client= boto3.client("s3","us-east-1")
    print("test")
    object_metadata = s3_client.head_object(Bucket=bucket_name, Key=file_name)

    print(object_metadata)

    if "x-amz-meta-customlabels" in object_metadata["ResponseMetadata"]["HTTPHeaders"]:
        customlabels = object_metadata["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-customlabels"].split(
            ",")
        for item in customlabels:
            item = item.strip()
            item = item.lower()
            if item not in labels:
                labels.append(item)
    
    print(labels)

    ####
    
    
    timestamp = datetime.now().strftime('%Y-%d-%mT%H:%M:%S')
    object = json.dumps({
        'objectKey' : file_name,
        'bucket' : bucket_name,
        'createdTimestamp' : timestamp,
        'labels' : labels
    })
    headers = {"Content-Type": "application/json"}
    url = '%s/%s/_doc/' % (host_url, index_name)
    response = requests.post(url, auth=credentials, data=object, headers=headers)
    print(response)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET',
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps("Image has been added successfully!")
    }
    
    
