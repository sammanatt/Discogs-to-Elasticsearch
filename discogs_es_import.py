import os
import sys
import json
import time
import certifi
import requests
import argparse
import pprint
import elasticsearch.helpers
from elasticsearch import Elasticsearch

pp = pprint.PrettyPrinter(indent=4)

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
    """
    Create a list of all existing _id values within Elascticsearch.
    """
    es_id_list = []
    get_ids = elasticsearch.helpers.scan(es,
                                        query={"query": {"match_all": {}}},
                                        index="discogs_"+args.user,
                                        )
    for i in get_ids:
        es_id_list.append(i['_id'])
    return es_id_list


def discogs_es_sync(discogs_username):
    existing_ids = get_all_ids()
    # Scan Discogs library
    page = 1
    albums = requests.get(url+"users/"+str(discogs_username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
    total_pages = albums["pagination"]["pages"]
    discogs_library = []
    while page <= total_pages:
        try:
            albums = requests.get(url+"users/"+str(discogs_username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
            for i in albums["releases"]:
                discogs_library.append(i['date_added'])
                #pp.pprint(i)
                #date added was selected as the es_id as it's the unique timestamp a user added the entry to their collection.
                es_id = i['date_added']
                if es_id in existing_ids:
                    print(f"Album already exists: {i['basic_information']['title']} by {i['basic_information']['artists'][0]['name']}")
                elif es_id not in existing_ids:
                    print(f"New album!!!  {i['basic_information']['title']}")
                    es.index(index='discogs_'+discogs_username, doc_type='_doc', id=es_id, body=i)
                elif discogs_library:
                    print("*** WRITE COMMAND TO DELETE FROM ELASTICSEARCH")
                time.sleep(3) #Sleep for discogs rate limiting (add auth to increase to 60 requests per minute)
            page = page + 1
        except requests.exceptions.ConnectionError:
            print("API refused connection.")
    # Delete Elasticsearch documents that no longer exist in Discogs library
    print("Running cleanup...")
    for i in existing_ids:
        if i not in discogs_library:
            #debug me! returning Make Yourself and Summer Pack. Should return Make Yourself and Bruce live
            print(f"this has got to go: {i}")
        else:
            print("No albums to delete.")


def main(args):
    discogs_es_sync(args.user)

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
