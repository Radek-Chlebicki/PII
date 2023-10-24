import dns.resolver
import dns.reversename
import argparse
import os
import multiprocessing
import json
import publicsuffixlist
import urllib.parse
import ipaddress
import socket
import time

def isIpAddr(aStr):
    isip = False
    try:
        ipaddress.IPv4Address(aStr)
        isip |= True
    except ValueError as e: 
        isip |= False
    try:
        ipaddress.IPv6Address(aStr)
        isip |= True
    except ValueError as e: 
        isip |= False
    return isip 

def resolverTest():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]
    answers = ""

    try : 
        answers = dns.resolver.resolve("0000.gofenews.com", "CNAME")
        answers = dns.resolver.resolve("gmail.com", "CNAME")
    except dns.resolver.NoAnswer as e:
        print(e)

    print(' query qname:', answers.qname, ' num ans.', len(answers))
    for rdata in answers:
        print(' cname target address:', rdata.target)

def decloakUrl(url : str):
    # print(f"url {url}, etld+1 {etld1}")
    psl = publicsuffixlist.PublicSuffixList()

    result = urllib.parse.urlparse(url)
    # print(result)
    domain = result.netloc
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8"]
    answers = ""
    hasCname= True
    cnames = [domain]
    endedInIp = False
    while  hasCname:     
        try : 
            if (isIpAddr(cnames[-1])):
                possibleDomain  = ""
                try:
                    result = dns.resolver.resolve(dns.reversename.from_address(cnames[-1]), "PTR")
                    possibleDomain = result[0].to_text()  # Return the first PTR record (hostname)
                    cnames.pop()
                    cnames.append(possibleDomain)
                except:
                    print("ends in ip address")
                    print(cnames)
                    hasCname = False
                    endedInIp = True
                    continue

            answers : dns.resolver.Answer = dns.resolver.resolve(cnames[-1], "CNAME")
            
            for rdata in answers:
                # print(rdata.target)
                cnames += [str(rdata.target)[:-1]]
                #consider this to be the last
        except dns.resolver.NoAnswer as e:
            # print("NO CNAME CASE")
            # print(e)
            hasCname = False
        except:
            hasCname = False
            
    
    # print(psl.privatesuffix(cnames[0]))
    # print(psl.privatesuffix(cnames[-1]))
        
    if endedInIp:
        cloaking = True
    else:
        cloaking =  psl.privatesuffix(cnames[0]) != psl.privatesuffix(cnames[-1])
        # cloaking = False
    
    return (cnames, cloaking)

def decloakHar(harPathOutFolder : tuple[str,str] ):
    harPath = harPathOutFolder[0]
    print(harPath)
    outFolder = harPathOutFolder[1]
    etld1 = os.path.basename(harPath)
    with open(harPath, mode="r") as hp:
        harJson  = json.load(hp)
    entries = harJson["log"]["entries"]

    cloakingCount = 0 
    for entry in entries:
        try:
            url = entry["request"]["url"]
            # same site but not same origin check ------------------------
            # example www.google.co.kr
            # urllib.parse.urlparse(url).hostname gives - www.google.co.kr
            #".".join("www.google.co.kr".split(".")[:-1]) gives www.google.co
            # psl.publicsuffix("www.google.co.in")
            # Out[19]: 'co.in'
            # In [20]: psl.privatesuffix("www.google.co.in")
            # Out[20]: 'google.co.in
            psl = publicsuffixlist.PublicSuffixList()
            hostname = urllib.parse.urlparse(url).hostname
            same_site = psl.privatesuffix(hostname) == psl.privatesuffix(etld1)
            same_origin = hostname.split(".")[0] == etld1.split(".")[0]

            if (same_site == True and same_origin==False):
                # print(".".join(etld1.split(".")[:-1]))
                # print(urllib.parse.urlparse(url).hostname)
                # print()
                # x = input(".")
                # time.sleep(0.5)
                cnames, cloaking = decloakUrl(url=url)
                entry["request"]["cnames"] = cnames
                entry["request"]["cloaking"] = cloaking
                if (cloaking):
                    cloakingCount += 1
        except KeyError as e:
            print(e)
            pass
            #ignore key error
    print(cloakingCount)

    with open(os.path.join(outFolder, etld1), "w") as op: 
        json.dump(harJson, op)
    return cloakingCount


def process(harFolder:str, outFolder:str):
    files = [file for file in os.listdir(harFolder)]
    paths = [os.path.join(harFolder, file) for file in files]
    harPathsOutFolder = [(path,outFolder) for path in paths if os.path.isfile(path)]
    pool = multiprocessing.Pool(3)
    print(harPathsOutFolder)
    for count in pool.imap(decloakHar, harPathsOutFolder):
        print(count)
    # map(decloakHar,harPathsOutFolder)
    # for path in harPathsOutFolder:
    #     decloakHar(path)
    #     print(path)
    pool.close()

def main():
    parser = argparse.ArgumentParser(description="decloak har entries")
    parser.add_argument("harFolder", help="folder with hars")
    parser.add_argument("outFolder", help="output folder for hars")
    args = parser.parse_args()
    harFolder : str = args.harFolder
    outFolder : str = args.outFolder
    process(harFolder, outFolder)

if __name__=="__main__":
    main()