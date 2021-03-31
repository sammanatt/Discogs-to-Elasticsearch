import os
import sys
import json
import time
import certifi
import requests
import argparse
from elasticsearch import Elasticsearch

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

elasticsearch_user = os.environ["elasticsearch_user"]
elasticsearch_password = os.environ["elasticsearch_password"]
elasticsearch_connection_string = os.environ["elasticsearch_connection_string"]
discogs_username = os.environ["discogs_username"]

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


# Importing Discogs library
url = "https://api.discogs.com/"

def discogs_full_import(discogs_username):
    page = 1
    es_id = 1
    albums = requests.get(url+"users/"+str(discogs_username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
    total_pages = albums["pagination"]["pages"]
    while page <= total_pages:
        albums = requests.get(url+"users/"+str(discogs_username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
        for i in albums["releases"]:
            print(i)
            es.index(index='discogs_'+discogs_username, doc_type='_doc', id=es_id, body=i)
            time.sleep(3) #Sleep for discogs rate limiting (add auth to increase to 60 requests per minute)
            print("this is ES ID: " + str(es_id))
            es_id += 1
        page = page + 1


def main(args):
        discogs_full_import(args.user)


if __name__ == "__main__":
        # Build argument parser
        parser = argparse.ArgumentParser(description='Send communcations to multiple customers via email.')
        parser.add_argument('-u',
                            '--user',
                          default=None,
                          help="Discogs user to import from.",
                          type=str)
        args = parser.parse_args()

        if args.user is None:
            args.user = discogs_username
            if len(discogs_username) < 1:
                exit('discogs_username is empty in the .env file. Update that variable or use the username argument (-u, --user) to provide username.')
        main(args)
