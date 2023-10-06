import os
import json 
from urllib.parse import urlparse
from adblockparser import AdblockRules
import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("csvLeakFile", help="the output of getLeaks.py")
    parser.add_argument("txtFilterRulesFile", help="for the adblockparser")
    parser.add_argument("outFileName", help="csv where block results shall be summarized(column amended to csvLeakFile)")
    args = parser.parse_args()
    process(args.csvLeakFile, args.txtFilterRulesFile, args.outFileName)

def process(csvLeakFilePath, txtFilterRulesFilePath, outFilePath):
    df = pd.read_csv(csvLeakFilePath)
    print(df.index)
    print(df.columns)
    columnName = os.path.basename(txtFilterRulesFilePath)
    with open(file=txtFilterRulesFilePath, mode="r")as fp:
        lines = fp.readlines()
        lines = [line.rstrip('\n') for line in lines]
    rules = AdblockRules(lines)
    df.third_party_url.fillna(value="",inplace=True)
    newCol = df.loc[:,"third_party_url"].map(lambda x: rules.should_block(x))
    df.insert(loc=len(df.columns),column=columnName, value=newCol)
    df.to_csv(outFilePath)
    
if __name__ == "__main__":
    main()
