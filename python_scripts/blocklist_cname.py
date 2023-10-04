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
    lines += file.readlines()
    
# with open("./adguard_filter.txt", "r") as file : 
#     lines += file.readlines()

    
lines = [line.rstrip('\n') for line in lines]

rules = AdblockRules(lines)

FOLDERNAME = "./general_news_cnames/"

fileNames = os.listdir(FOLDERNAME)

piiJsons = []
for fname in fileNames: 
    file = open(FOLDERNAME + fname, 'r') 
    theJson = json.load(file)
    for singleSiteJson in theJson:
        singleSiteJson["fname"] = fname
    piiJsons.append(theJson)

with open("./cnames_easyprivacy.csv", "w") as file : 
    for singleSiteJson in piiJsons:
        for leakageInstance in singleSiteJson: 
            if (leakageInstance["str"] != "60201" and leakageInstance["str"] != "Evanston" and leakageInstance["str"] != "Illinois" and leakageInstance["str"] != "NjAyMD" and leakageInstance["str"] != "RXZhbnN0b2" and leakageInstance["str"] != "SWxsaW5vaX") :
                possible_violators = [leakageInstance["url"]] + leakageInstance["cNames"]
                for pv in possible_violators: 
                
                    shouldblock = rules.should_block(pv)
                    method = check_method(leakageInstance)
                    fullUrl = leakageInstance["url"]
                    theUrl = urlparse(leakageInstance["url"]).netloc
                    stringLeaked = leakageInstance["str"]
                    cNames = leakageInstance["cNames"]
                    fname = leakageInstance["fname"]
                    if (shouldblock):
                        for rule in rules.rules:
                            if (str(rule.raw_rule_text).find(pv) != -1):
                                print("Matched rule: " + rule.raw_rule_text, end=", ", file=file)
                                break
                        print(f"{method}, {pv}, {stringLeaked}, {cNames}, {fname}", file=file)

