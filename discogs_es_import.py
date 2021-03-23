import requests
import json
from elasticsearch import Elasticsearch
import certifi
import time
import sys
import os

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

elasticsearch_user = os.environ["elasticsearch_user"]
elasticsearch_password = os.environ["elasticsearch_password"]
elasticsearch_connection_string = os.environ["elasticsearch_connection_string"]

# Connecting to ES
try:
    es = Elasticsearch([str(elasticsearch_connection_string)],
        http_auth=(elasticsearch_user,elasticsearch_password),
        port=4105,
        use_ssl=True,
        verify_certs=True,
        ca_certs=certifi.where(),
    )
    print("Connected {}".format(es.info()))
except Exception as ex:
    print("Error: {}".format(ex))


# Importing Disogs library
username = str(sys.argv[1])
url = "https://api.discogs.com/"

def discogs_import(username):
    page = 1
    es_id = 1
    albums = requests.get(url+"users/"+str(username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
    total_pages = albums["pagination"]["pages"]
    while page <= total_pages:
        albums = requests.get(url+"users/"+str(username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
        for i in albums["releases"]:
            print(i)
            es.index(index='discogs_'+username, doc_type='_doc', id=es_id, body=i)
            time.sleep(3) #Sleep for discogs rate limiting (add auth to increase to 60 requests per minute)
            print("this is ES ID: " + str(es_id))
            es_id += 1
        page = page + 1


discogs_import(username)
