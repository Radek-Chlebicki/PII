import requests
from bs4 import BeautifulSoup
import os
import json
import time
from lxml.html import fromstring
import requests
from itertools import cycle
import traceback
import random
import secrets
import csv
import argparse


parser  = argparse.ArgumentParser(description="Takes tranco csv and queries mcaffee, and gives json with key value as such  \"google.com\": [2, \"Search Engines\"] ")
parser.add_argument("tranco_csv_path")
parser.add_argument("out_json_path")
parser.add_argument("number_of_sites_to_categorize")

args = parser.parse_args()
tranco_csv_path = args.tranco_csv_path
out_json_path = args.out_json_path
numSites = int(args.number_of_sites_to_categorize)
if (numSites %100 != 0):
     parser.error("number of sites must be multiple of 100")


"""
visit to sitelookup.mcafee.com/sources/index.pl gets some
tokens and headers that are needed for the form requests
"""
def setup():
    headers = {
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5)',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language' : 'en-US,en;q=0.9,de;q=0.8'
    }

    base_url = 'http://sitelookup.mcafee.com/sources/index.pl'
    r = requests.get(base_url, headers=headers)

    bs = BeautifulSoup(r.content, "html.parser")
    form = bs.find("form", { "class" : "contactForm" })
    token1 = form.find("input", {'name': 'e'}).get('value')
    token2 = form.find("input", {'name': 'c'}).get('value')
    headers['Referer'] = base_url
    return headers, token1, token2

"""
Using headers and token ask to check this url

"""
def lookup(headers, token1, token2, url):
    payload = {'e':(None, token1),
               'c':(None, token2),
               'action':(None,'checksingle'),
               'product':(None,'01-ts'), #mcafee realtime database 
               'url':(None, url)}
    r = requests.post('https://sitelookup.mcafee.com/en/feedback/url', headers=headers, files=payload)

    bs = BeautifulSoup(r.content, "html.parser")
    form = bs.find("form", { "class" : "contactForm" })

    table = bs.find("table", { "class" : "result-table" })
    td = table.find_all('td')
    categorized = td[len(td)-3].text
    category = td[len(td)-2].text[2:]
    risk = td[len(td)-1].text

    return categorized, category, risk

def runMcafeeTool():
    if not os.path.exists(out_json_path):
      os.mkdir(out_json_path)
    headers, token1, token2 = setup()
    _dict={}
    with open(tranco_csv_path,"r") as trancoCsv:
        readerCsv = csv.reader(trancoCsv)
        x=0 # this is the number of the site in the tranco, count 
        for row in readerCsv:
            #row has structure 300,espn.com
            #every 100 sites write to file and clear working dict
            #every 100 sites we get new headers and tokens
            # print(row)
            if x%100==0 :
                print(f"{x} done request new headers")
                time.sleep(3)
                headers, token1, token2 = setup()
                print(f"e: {token1}, c: {token2}  ")
                with open(out_json_path, 'a') as fp:
                    print("", file=fp)
                    json.dump(_dict, fp)
                _dict = {}
                # stop once this many sites are reached 
                if x == numSites:
                    break

            url=row[1]
            # url = input('Enter a valid domain / url to check: ')
            try:
                categorized, category, risk = lookup(headers, token1, token2, url)
                print (x,url,category)
                _dict[url]=(x,category)
            except Exception as e:
                print (str(e)) 
                _dict[url]=(x,"Error: " + str(e))
            x+=1          
    

if __name__ == "__main__":
    runMcafeeTool()

    

