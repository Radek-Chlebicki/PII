import os
import json 
from urllib.parse import urlparse

from adblockparser import AdblockRules



def check_method(anInstance):
    if (anInstance["GET"] != ""):
        return "get"
    elif (anInstance["POST"] != ""):
        return "post"
    elif ((anInstance["referer"] != "")):
        return "referer"
    elif (anInstance["cookie"] != ""):
        return "cookie"
    else:
        return "undeterminedmethod"

lines = []
with open("./easyprivacy.txt", "r") as file : 
    lines = file.readlines()
    lines = [line.rstrip('\n') for line in lines]

rules = AdblockRules(lines)

fileNames = os.listdir("./general_news_outs")

piiJsons = []
for fname in fileNames: 
    file = open("./general_news_outs/" + fname, 'r') 
    piiJsons.append(json.load(file))

for singleSiteJson in piiJsons:
    for leakageInstance in singleSiteJson: 
        if (leakageInstance["str"] != "60201" or leakageInstance["str"] != "Evanston" or leakageInstance["str"].s"Illinois" or \
                leakageInstance["str"] != "NjAyMD" or leakageInstance["str"] != "RXZhbnN0b2" or leakageInstance["str"] != "SWxsaW5vaX") :
            shouldblock = rules.should_block(leakageInstance["url"])
            method = check_method(leakageInstance)
            third_party = urlparse(leakageInstance["url"]).netloc
            stringLeaked = leakageInstance["str"]
            print(f"{shouldblock}, {method}, {third_party} , {stringLeaked}")

