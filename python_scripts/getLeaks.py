import haralyzer as haralyzer
import csv as csv
import json as json
import os as os
import pandas as pd 
import argparse 
import urllib.parse
from urllib.parse import unquote
import multiprocessing
import traceback
from adblockparser import AdblockRules
import ast

# import demjson3

def main():
    parser = argparse.ArgumentParser(description="find leakages to third parties in the HAR")

    parser.add_argument("harFolder", help="folder with hars, har file name is etld/hostname")
    parser.add_argument("hashCsv", help="csv with the hashes")
    parser.add_argument("outLeakCsvPath", help="output csv listing leaks")

    args = parser.parse_args()
    harFolder : str = args.harFolder
    hashCsvPath : str = args.hashCsv
    outLeakCsvPath : str = args.outLeakCsvPath
    process(harFolder, hashCsvPath, outLeakCsvPath)

def getHeaderValue(headers : list[dict[str,str]], name : str):
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return None

def getCookieValue(cookies : list[dict[str,str]], name : str):
    for cookie in cookies:
        if cookie["name"].lower() == name.lower():
            return cookie["value"]
    return None
# def searchDictListDf(dictList, df : pd.DataFrame):
#     for rowI in range(0, len(df.index)):
def findAll(aString, subString):
    start = 0
    while True: 
        start = aString.find(subString,start)
        if start == -1:
            return
        yield start
        start += len(subString)

def searchDictListAHash(dictList : list[dict[str,str]], aHash : str, col :str):
    # exclude = ["base64","base32","base16"]
    # if (not any(col in e for e in exclude)) and len(aHash) > 20:
    #     aHash = aHash[0:10]
    retlist : list[tuple(str,str)] = [] 
    for aDict in dictList: 
        key = unquote(unquote(unquote(aDict["name"])))
        value = unquote(unquote(unquote(aDict["value"])))
        keyFinds = list(findAll(key, aHash))
        valueFinds = list(findAll(value, aHash))
        if len(keyFinds) > 0 :
            retlist += [("key", key, value, keyFinds)]
        if len(valueFinds) > 0:
            retlist += [("value", key, value, valueFinds)]
    # if len(retlist) >0 : print(retlist)

    return retlist


def iterateTheHashesDictList(df : pd.DataFrame, dictList : list[dict[str,str]], method:str):
    if method == "cookie":
        # print("cookie")
        pass
    retlist = []
    for col in df.columns:
        for row in df.index:
            aHash = df.loc[row,col]
            # if col=="sha1": print(f"body{row},{col},{aHash}.")
            instances = searchDictListAHash(dictList, aHash, col)
            retlist += [{"where": where, "key": k, "value": v, "mimeType" : "", "text" : "", "index" : index ,"row": row, "col" : col, "hash" : aHash, "method" : method} for where, k, v, indexFinds in instances for index in indexFinds]

        if col == "plaintext" or col == "base16" or col == "base32" or col == "base64": 
            retlist.sort(key=lambda x : len(x["hash"]),reverse=True)
            # if len(retlist) > 0 : print(retlist)
            toRemove = []
            for i in range(0,len(retlist)): 
                for j in range(i,len(retlist)): 
                    if (len(retlist[i]["hash"]) > len(retlist[j]["hash"]) and retlist[i]["index"] + len(retlist[i]["hash"]) >= retlist[j]["index"] + len(retlist[j]["hash"])):
                        toRemove.append(j)
            toRemove = list(set(toRemove))
            # if len(toRemove) > 0 : print(toRemove)
            retlist = [elem for index, elem in enumerate(retlist) if index not in toRemove]
    
    return retlist

def searchBodyAHash(text : str, mimeType : str, aHash : str, col : str):
    # exclude = ["base64","base32","base16"]
    # if (not any(col in e for e in exclude)) and len(aHash) > 20:
    #     aHash = aHash[0:10]
    if mimeType == "application/x-www-form-urlencoded": 
        text = urllib.parse.unquote(urllib.parse.unquote(urllib.parse.unquote(text)))
    indexList = list(findAll(text, aHash))
    return indexList

def iterateTheHashesBody(df : pd.DataFrame, text : str, mimeType : str, method:str):
    # print(mimeType)
    retlist = []
    for col in df.columns:
        for row in df.index:
            aHash = df.loc[row,col]
            # if col=="sha1": print(f"body{row},{col},{aHash}.")

            # if col == "plaintext" : print(aHash)
            occuranceIndexes = searchBodyAHash(text, mimeType, aHash, col)
            retlist += [{"where": "body", "key" : "", "value": "", "mimeType": mimeType, "text": text, "index": index, "row": row, "col" : col, "hash" : aHash, "method" : method} for index in occuranceIndexes]

        if col == "plaintext" or col == "base16" or col == "base32" or col == "base64": 
            retlist.sort(key=lambda x : len(x["hash"]),reverse=True)
            # if len(retlist) > 0 : print(retlist)
            toRemove = []
            for i in range(0,len(retlist)): 
                for j in range(i,len(retlist)): 
                    if (len(retlist[i]["hash"]) > len(retlist[j]["hash"]) and retlist[i]["index"] + len(retlist[i]["hash"]) >= retlist[j]["index"] + len(retlist[j]["hash"])):
                        toRemove.append(j)
            toRemove = list(set(toRemove))
            # if len(toRemove) > 0 : print(toRemove)
            retlist = [elem for index, elem in enumerate(retlist) if index not in toRemove]
            
    return retlist


def getLeakTemplate():
    return {
        "first_party" : "", 
        "pageref"     : "",
        "third_party" : "", 
        "third_party_url" : "",
        "http_method" : "",
        "startedDateTime" : "",
        "leak_method" : "", # header, cookie, get, post
        "encoding"  : "",
        "plain_pii" : "",
        "raw_pii": "",
        "where" : "",
        "key" : "", 
        "value" : "", 
        "mimeType" : "", 
        "text" : "",
        "index" : "",
        "cloaking" : "",
        "cloak_list" : []        
    }
def str_to_list(s):
    print(s)
    return ast.literal_eval(s)

def entryToLeak(entry, hashDf, firstParty,pages):
    leak = getLeakTemplate()
    cloaked = False 
    try: 
        cloaked = entry["request"]["cloaking"]
    except KeyError as e: 
        cloaked = False

    cloakList = []
    try: 
        cloakList = entry["request"]["cnames"]
    except KeyError as e: 
        cloakList = False
    http_method = entry["request"]["method"]
    first_party = firstParty
    third_party_url = entry["request"]["url"]
    if not cloaked:
        third_party = urllib.parse.urlparse(entry["request"]["url"]).hostname
    else: 
        lastCname = entry["request"]["cnames"][-1]
        third_party = lastCname
    startedDateTime = entry["startedDateTime"]
    pageref = ""
    try:
        pageref = entry["pageref"]
    except KeyError:
        # print("keyerror no pageref: " + firstParty)
        pass
    if pageref != "":
        for page in pages:
            if page["id"] == pageref: 
                pageref = page["title"]

    if (not ("GET" in entry["request"]["method"]  or  "POST" in entry["request"]["method"]) ):
        return []
    
    queryLeaks = iterateTheHashesDictList(hashDf, entry["request"]["queryString"], "get")

    cookieLeaks = iterateTheHashesDictList(hashDf, entry["request"]["cookies"], "cookie")

    headerLeaks  = iterateTheHashesDictList(hashDf, entry["request"]["headers"], "header")

    bodyLeaks = []
    try: 
        bodyLeaks = iterateTheHashesBody(hashDf, entry["request"]["postData"]["text"], entry["request"]["postData"]["mimeType"], "post" )
    except KeyError: 
        pass

    leaksList = []
    for aFind in queryLeaks + cookieLeaks + headerLeaks + bodyLeaks:
        leakInstance = getLeakTemplate()
        leakInstance["first_party"] = first_party
        leakInstance["pageref"] = pageref
        leakInstance["third_party"] = third_party
        leakInstance["third_party_url"] = third_party_url
        leakInstance["http_method"] = http_method
        leakInstance["startedDateTime"] = startedDateTime
        leakInstance["leak_method"] = aFind["method"]
        leakInstance["encoding"] = aFind["col"]
        leakInstance["plain_pii"] = aFind["row"]
        leakInstance["where"] = aFind["where"]
        leakInstance["index"] = aFind["index"]
        leakInstance["key"] = aFind["key"]
        leakInstance["value"] = aFind["value"]
        leakInstance["mimeType"] = aFind["mimeType"]
        leakInstance["text"] = aFind["text"]
        leakInstance["cloaking"] = cloaked
        leakInstance["cloak_list"] = cloakList
        leaksList.append(leakInstance)    

    return leaksList

def thirdPartyTest(anEntry, firstParty):
    openThirdParty = not (firstParty in urllib.parse.urlparse(anEntry["request"]["url"]).hostname)
    try: 
        cloaked = anEntry["request"]["cloaking"]
    except KeyError as e: 
        cloaked = False
        print(e)
    return openThirdParty or cloaked

def harToLeaks(aTup):
    harPath = aTup[0]
    harFolder = aTup[1]
    hashDf = aTup[2]

    firstParty = harPath.rsplit(".",1)[0]
    print(firstParty)
    harJson = None
    with open(os.path.join(harFolder,harPath), mode="r") as aHar:
        try : 
            harJson = json.load(aHar)
        except json.JSONDecodeError as e:
            print(e)
            traceback.print_exc()

    pages = harJson["log"]["pages"]
    allEntries = harJson["log"]["entries"]
    
    allEntriesWithRequests = list(filter(lambda anEntry : "request" in anEntry,allEntries))
    
    thirdPartyEntries = list(filter(lambda entry : thirdPartyTest(entry, firstParty), allEntriesWithRequests))
    
    leaks = []
    aLeak = getLeakTemplate()
    aLeak["first_party"] = firstParty
    leaks.append(aLeak)
    
    for entry in thirdPartyEntries: 
        leaksList = entryToLeak(entry, hashDf, firstParty, pages)
        leaks.extend(leaksList)
    
    return leaks

def process(harFolder, hashCsvPath, outLeakCsvPath:str):
    harPathList : list[str] = [harPath for harPath in os.listdir(harFolder) if  os.path.isfile(os.path.join(harFolder,harPath)) ]    
    # harPathList = harPathList[0:5]
    # harPathList = ["/home/chootiya/printing/classes/445_fabian/zarc2/general_news_hars/theatlantic.com.har"]
    with open(hashCsvPath, mode="r") as hashFile : 
        reader = csv.reader(hashFile)
        columns = next(reader)
        hashDf = pd.DataFrame(columns=columns) #in csv the index column has no header
        index = []
        for row in reader:
            if len(row) != 0:
                index.append(row[0])
                toappend = pd.DataFrame([row], columns=columns)
                hashDf = pd.concat([hashDf, toappend],ignore_index=True)
        hashDf.set_index(hashDf.columns[0], inplace=True) 
        
    print("hashdf to follow: ")
    print(hashDf.head(25))
    
    pool = multiprocessing.Pool(14)

    harPathList = [(harPath, harFolder, hashDf) for harPath in harPathList]
    resultsDf = pd.DataFrame([getLeakTemplate()])
    for harLeakList in pool.imap(harToLeaks,harPathList):
        for leak in harLeakList:
            resultsDf = pd.concat([resultsDf, pd.DataFrame([leak])],ignore_index=True)
    pool.close()

    print(resultsDf.head(20))
    resultsDf.to_csv(outLeakCsvPath)



if __name__ == "__main__":
    main()