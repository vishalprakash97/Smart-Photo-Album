import json
import boto3
import os
import datetime
import time
import requests
import urllib
import inflect

p = inflect.engine()

credentials = (os.environ["username"],os.environ["password"])
host_url = os.environ["host_url"]
index_name = 'photos'
type_name = 'Photo'
region = 'us-east-1' 
service = 'es'

headers = {"Content-Type": "application/json"}
url = "%s/%s/_search" % (host_url, index_name)

def speech():
    transcribe = boto3.client('transcribe')
    
    job_name = datetime.datetime.now().strftime("%m-%d-%y-%H-%M%S")
    job_uri = "s3://photoalbum-audiosearch-a2/Recording.wav"
    storage_uri = "photoalbum-audiototext-a2"
    
    s3 = boto3.client('s3')
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='en-US',
        OutputBucketName=storage_uri
    )
    
    #status = transcribe.get_transcription_job(
    #        TranscriptionJobName=job_name)
    i = 0
    while i < 60:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        i += 1
        time.sleep(5)

    print("Transcript URL: ", status)
    
    job_name = str(job_name) + '.json'
    #print(job_name)
    obj = s3.get_object(Bucket=storage_uri, Key=job_name)
    #print("Object : ", obj)
    body = json.loads(obj['Body'].read().decode('utf-8'))
    print("Body :", body['results']['transcripts'][0]['transcript'])
    
    return body['results']['transcripts'][0]['transcript']

def lambda_handler(event, context):
    # TODO implement
    print(event)
    if not event.get('userid'):
        event['userid'] = 'IAM_Temp_User'
    #print(event)
    query=event['params']['querystring']['q']
    #query = event['messages'][0]['unstructured']['text']
    #query = event["queryStringParameters"]["q"]
    
    if query == 'searchAudio':
        query = speech()
    
    print('Query = ', query)
    lex = boto3.client("lex-runtime", region_name="us-east-1")
    
    query = query.replace('.', '')
    
    lex_resp = lex.post_text(
        botName='SearchAlbumTwo',
        botAlias='AlbumBotTwo',
        userId=event['userid'],
        inputText=query)
        
    searchone = lex_resp['slots']['SearchOne']
    searchtwo = lex_resp['slots']['SearchTwo']
    
    if p.singular_noun(searchone):
        searchone = p.singular_noun(searchone)
    if searchtwo is not None and p.singular_noun(searchtwo):
        searchtwo = p.singular_noun(searchtwo)
    
    print(searchone)
    print(searchtwo)
    
    queries = list()
    result = list()
    
    queries.append(searchone)
    if searchtwo is not None:
        queries.append(searchtwo)
    
    #queries = lex_resp['message'].split('-')
    
    for query in queries:
        print(query)
        
        es_query = {
            "query": {
                "match": {
                    "labels": query
                }
            }
        }
        print(es_query)
        
        response = json.loads(requests.get(url,
                                              auth=credentials,
                                              headers=headers,
                                              data=json.dumps(es_query)).content.decode('utf-8'))
        
        
        for photo in response['hits']['hits']:
            key = photo['_source']['objectKey']
            url_res = "https://photoalbum-a2.s3.amazonaws.com/"+key

            if (url_res not in result):
                result.append(url_res)

        #print(result)
    print(result)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,PUT',
            'Access-Control-Allow-Credentials': 'true'
        }
    }
    #return None