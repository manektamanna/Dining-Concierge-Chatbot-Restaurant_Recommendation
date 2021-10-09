
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import json
import boto3
import random
import logging
from boto3.dynamodb.conditions import Key
import requests
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# The function return list of 3  random  business ids matching our cuisine
def findRestaurantFromElasticSearch(cuisine):
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'search-restaurants1-yyu3b45gf5jcj5iva64ghur5sm.us-east-1.es.amazonaws.com'
    index = 'restaurants'
    url = 'https://' + host + '/' + index + '/_search'
    query = {
        "size": 1600,
        "query": {
            "query_string": {
                "default_field": "genres",
                "query": cuisine
            }
        }
    }
    headers = { "Content-Type": "application/json" }
    response = requests.get(url,auth=awsauth, headers=headers, data=json.dumps(query))
    res = response.json()
    noOfHits = res['hits']['total']
    hits = res['hits']['hits']
    buisinessIds = []
    for hit in hits:
        buisinessIds.append(str(hit['_source']['id']))
    return random.sample(buisinessIds,3)

# function returns detail of all resturantids as a list(working)
#Get restaurant values using IDs obtained
def getRestaurantFromDb(restaurantIds):
    res = []
    client = boto3.resource('dynamodb')
    table = client.Table('yelp-restaurants')
    for id in restaurantIds:
        response = table.query(
        KeyConditionExpression=Key('id').eq(id))
        
        res.append(response)
        z = []
        for val in res:
            z.append([val['Items'][0]['name'],val['Items'][0]['address']])
    return z

    
def sendEmail(restaurants,recommendationRequest):
    # This address must be verified with Amazon SES.
    SENDER = "tm3734@nyu.edu"
    RECIPIENT = recommendationRequest['email']['stringValue']
    AWS_REGION = "us-east-1"
    # The subject line for the email.
    SUBJECT = "Restaurant Recommendations for you!"
    CUISINE=recommendationRequest['cuisine']['stringValue']
    PEOPLE=recommendationRequest['people']['stringValue']
    DATE=recommendationRequest['date']['stringValue']
    TIME=recommendationRequest['time']['stringValue']
    
        
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "Hello! Here are my " + str(CUISINE) + " restaurant suggestions for " + str(PEOPLE) + " people, for " + str(DATE) + " at " + str(TIME) + "\n\n" + "1. " + str(restaurants[0][0]) + ", located at " + str(restaurants[0][1]) + "\n\n" + "2. " + str(restaurants[1][0]) + ", located at " + str(restaurants[1][1]) + "\n\n" + "3. " + str(restaurants[2][0]) + ", located at " + str(restaurants[2][1]) + "\n\n" + "Enjoy your meal!"
    CHARSET = "UTF-8"
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                  
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
           
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        


def lambda_handler(event, context):
    print("event : ",event)
    recommendationRequest = event['Records'][0]['messageAttributes']
    print(".... : ",recommendationRequest)
    print("cusine : ",recommendationRequest['cuisine']['stringValue'])
    print("location : ", recommendationRequest['location']['stringValue'])
    logger.debug("Recommendation request is {}".format(recommendationRequest))
    cuisine=recommendationRequest['cuisine']['stringValue']
    ids = findRestaurantFromElasticSearch(cuisine)
    restaurants = getRestaurantFromDb(ids)
    print("Restaurants : ",restaurants)
    response =sendEmail(restaurants,recommendationRequest)
    return {
        'statusCode': 200,
        'body': response
    }
