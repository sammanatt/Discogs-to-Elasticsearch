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


def gimme_5(username):
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
    for i in range(5):
        print(random.choice(album_list))

def main(args):
    #print(f"args.user is: {args.user}")
    gimme_5(args.user)

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
