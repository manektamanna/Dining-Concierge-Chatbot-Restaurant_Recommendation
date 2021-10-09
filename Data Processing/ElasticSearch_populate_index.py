#Import relevant libraries involving authentication as well
import csv
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import boto3
from botocore.vendored import requests

#Define parameters before establishing a connection
region = 'us-east-1' 
service = 'es' #Elasticsearch service
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'ABCDE' #Insert your host values from elastic search instance created                                            #'search-restaurants1-yyu3b45gf5jcj5iva64ghur5s-m.us-east-1.es.amazonaws.com'

#Establish a connection with your elastic search domain created on AWS
es = Elasticsearch(
    hosts = [{'host':host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)

#Read values from existing CSV of scraped data
#Populate elastic search with restaurant IDs and their cuisine types
with open('restaurant_details.csv', newline='') as f:
    reader = csv.reader(f)
    restaurants = list(reader)

try:
    #Define a starting point for your IDs which increments after every loop iteration
    i = 1
    for restaurant in restaurants:
        index_data = {
            'id': restaurant[0],
            'genres': restaurant[5]
        }
 
        es.index(index="restaurants",id=i, document=index_data, refresh=True) 
        i+=1
except Exception as e:
    print(e)
