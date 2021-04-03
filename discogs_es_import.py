import os
import sys
import json
import time
import certifi
import requests
import argparse
import elasticsearch.helpers
from elasticsearch import Elasticsearch

# Load environment file, assign variables
from dotenv import load_dotenv
load_dotenv()

elasticsearch_user = os.environ["elasticsearch_user"]
elasticsearch_password = os.environ["elasticsearch_password"]
elasticsearch_connection_string = os.environ["elasticsearch_connection_string"]
elasticsearch_port = os.environ["elasticsearch_port"]
discogs_username = os.environ["discogs_username"]

# Connecting to ES
try:
    es = Elasticsearch([str(elasticsearch_connection_string)],
        http_auth=(elasticsearch_user,elasticsearch_password),
        port=elasticsearch_port,
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
    albums = requests.get(url+"users/"+str(discogs_username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
    total_pages = albums["pagination"]["pages"]
    while page <= total_pages:
        try:
            albums = requests.get(url+"users/"+str(discogs_username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
            for i in albums["releases"]:
                print("\n" + i + "\n")
                es_id = i['date_added']
                es.index(index='discogs_'+discogs_username, doc_type='_doc', id=es_id, body=i)
                time.sleep(3) #Sleep for discogs rate limiting (add auth to increase to 60 requests per minute)
            page = page + 1
        except requests.exceptions.ConnectionError:
            print("API refused connection.")


def get_all_ids():
    es_id_list = []
    get_ids = elasticsearch.helpers.scan(es,
                                        query={"query": {"match_all": {}}},
                                        index="discogs_"+args.user,
                                        )
    for i in get_ids:
        es_id_list.append(i['_id'])
    print(len(es_id_list))


def discogs_import_new_entries(discogs_username):
    # Scan Discogs library
    page = 1
    albums = requests.get(url+"users/"+str(discogs_username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
    total_pages = albums["pagination"]["pages"]
    while page <= total_pages:
        try:
            albums = requests.get(url+"users/"+str(discogs_username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
            for i in albums["releases"]:
                print("\n" + i + "\n")
                #date added was selected as the es_id as it's the unique timestamp a user added the entry to their collection.
                es_id = i['date_added']
                #es.index(index='discogs_'+discogs_username, doc_type='_doc', id=es_id, body=i)
                time.sleep(3) #Sleep for discogs rate limiting (add auth to increase to 60 requests per minute)
            page = page + 1
        except requests.exceptions.ConnectionError:
            print("API refused connection.")


def main(args):
        #discogs_full_import(args.user)
        get_all_ids()

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
