import json
import requests
import argparse
import random
import os
import sys

#To run this script from the cli type: python discogs.py "USERNAME"
from dotenv import load_dotenv
load_dotenv()

discogs_username = os.environ["discogs_username"]
#username = str(sys.argv[1])

url = "https://api.discogs.com/"

def discogs_user_verification():
    """
    Validates that the supplied username exists within Discogs.
    """
    url = "https://api.discogs.com/"
    user_collection = requests.get(url+"users/"+str(args.user)+"/collection/folders/0")
    if user_collection.status_code == 200:
        collection_string = user_collection.json()
        collection_count = collection_string['count']
        return collection_count
    else:
        exit(f"\nERROR {user_collection.status_code}: {user_collection.json()['message']} \nPlease check for typos in Discogs username or sign up for an account at: https://accounts.discogs.com/register?login_challenge=5cc9a3696af745a2a1f7ac4d523de053")

def gimme_5(username, records_to_return):
    page = 1
    albums = requests.get(url+"users/"+str(username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
    total_pages = albums["pagination"]["pages"]
    album_list = []
    while page <= total_pages:
        albums = requests.get(url+"users/"+str(username)+"/collection/folders/0/releases?page="+str(page)+"&per_page=100").json()
        for i in albums["releases"]:
            entry = i["basic_information"]["title"] + " by "+ i["basic_information"]["artists"][0]["name"]
            album_list.append(entry)
        page = page + 1
    for i in range(records_to_return):
        print(random.choice(album_list))



def main(args):
    discogs_user_verification()
    gimme_5(args.user,args.records)

if __name__ == "__main__":
        # Build argument parser
        parser = argparse.ArgumentParser(description='Send communcations to multiple customers via email.')
        parser.add_argument('-u',
                            '--user',
                          help="Discogs user to import from.",
                          type=str)
        parser.add_argument('-r',
                            '--records',
                            '-c',
                            '--count',
                          help="Adjusts the number of records to return.",
                          type=int,
                          default=5)
        args = parser.parse_args()

        if args.user is None:
            args.user = discogs_username
            if len(discogs_username) < 1:
                exit('discogs_username is empty in the .env file. Update that variable or use the username argument (-u, --user) to provide username.')
        main(args)
