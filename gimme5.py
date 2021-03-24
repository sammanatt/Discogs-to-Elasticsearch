import json
import requests
import random
import sys

#To run this script from the cli type: python discogs.py "USERNAME"
username = str(sys.argv[1])

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

gimme_5(username)
