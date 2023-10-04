import json 
import argparse 

CATEGORY_I = 1
RANK_I = 0

# W95J9
# Q9PP4
# VXL5N

parser = argparse.ArgumentParser(description="Takes a json with kv format such as \"google.com\": [2, \"Search Engines\"] and gives a json where k is \"Search Engines\" category and v is list of [2, \"google.com\"]")
parser.add_argument("site_category_json", help="format as  \"google.com\": [2, \"Search Engines\"]")
parser.add_argument("out_json" , help="key is category v is a list of [2, \"google.com\"]")
args = parser.parse_args()

with open("./data/categorizedWebsites-VXL5N.json") as f:
    theJsonList = json.load(f)
    # print(theJsonList)
    category_dict = {}
    for obj in theJsonList:

        for website in obj:
            # print(key)
            # print(obj[key])

            split_categories = obj[website][CATEGORY_I].split("- ")
            for aCat in split_categories: 
                if (not (aCat in category_dict.keys())):
                    category_dict[aCat] = []
                category_dict[aCat] += [ [obj[website][RANK_I] , website]]

        if (obj[website][RANK_I] == 9999):
            break
    with open("data/byCategoryVXL5N_2.json", 'w') as fp:
        json.dump(category_dict, fp=fp)
        # print("{", end="",file=fp)
        # for key in category_dict:
        #     print( str(key).replace("\'","\"") + " : " + str(category_dict[key]), file=fp, end=",\n")
        # print("}", end="",file=fp)
        # pass
    
        