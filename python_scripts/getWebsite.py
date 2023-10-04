import haralyzer
import json 
import argparse
import urllib.parse

def main():
    parser = argparse.ArgumentParser(description="get root website from HAR file")
    parser.add_argument("HAR_PATH", help="the path to har file")
    args = parser.parse_args()
    harPath = args.HAR_PATH
    bestGuessHost(harPath)

def bestGuessHost(harPath):
    with open(harPath,"r") as f:
        harParser = haralyzer.HarParser(json.loads(f.read()))

    urls = [page.url for page in harParser.pages]
    hostnames = [(urllib.parse.urlparse(url)).hostname for url in urls]
    bestGuess = min(hostnames, key=len)
    # print(bestGuess)
    return bestGuess

if __name__ == "__main__":
    main()