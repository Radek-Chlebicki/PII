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
    parser.add_argument("outLeakCsvPath", help="output csv listing leaks")

    args = parser.parse_args()
    harFolder : str = args.harFolder
    hashCsvPath : str = args.hashCsv
    outLeakCsvPath : str = args.outLeakCsvPath
    process(harFolder, hashCsvPath, outLeakCsvPath)






def harToTimes(aTup):
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
    
    times = []
    
    for entry in thirdPartyEntries: 
        times.append(entry["startedDateTime"])
    
    return times


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
    resultsDf = pd.DataFrame(columns=["req_times"])
    for harLeakList in pool.imap(harToTimes,harPathList):
        for leak in harLeakList:
            resultsDf = pd.concat([resultsDf, pd.DataFrame([leak])],ignore_index=True)
    pool.close()

    print(resultsDf.head(20))
    resultsDf.to_csv(outLeakCsvPath)
