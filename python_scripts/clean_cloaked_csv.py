import pandas as pd
import ast

def str_to_list(s):
    return ast.literal_eval(s)
str_to_list("['dpm.demdex.net', 'gslb-2.demdex.net', 'edge-va6.demdex.net', 'dcs-edge-va6-802167536.us-east-1.elb.amazonaws.com']")

#import the findings
# df = pd.read_csv("hars_general_news_cloak.csv", converters={"cloak_list":str_to_list})
# df = pd.read_csv("hars_entertainment_cloak.csv", converters={"cloak_list":str_to_list})
# df = pd.read_csv("hars_games_cloak.csv", converters={"cloak_list":str_to_list})
# df = pd.read_csv("hars_online_shopping_cloak.csv", converters={"cloak_list":str_to_list})
# df = pd.read_csv("hars_sports_cloak.csv", converters={"cloak_list":str_to_list})
df = pd.read_csv("hars_travel_cloak.csv", converters={"cloak_list":str_to_list})

# for csv in ["../hars_entertainment_out.csv", "../hars_online_shopping_out.csv", "../hars_sports_out.csv", "../hars_sports_out.csv", "../hars_games_out.csv", "../hars_travel_out.csv"]: 
#     df = pd.concat([df,pd.read_csv(csv)],ignore_index=True)
    
# for csv in ["../hars_entertainment_out.csv", "../hars_online_shopping_out.csv", "../hars_sports_out.csv", "../hars_sports_out.csv", "../"]
# remove location related leakages 
dropIndex = df[ (df["plain_pii"]=="60201") | (df["plain_pii"]=="Illinois") | (df["plain_pii"]=="Evanston") | (df["third_party"].isna())].index
df.drop(labels=dropIndex,axis=0,inplace=True)
df.reset_index(inplace=True, drop=True)
df.head()
def update_third_party(row):
    if row['cloaking']:
        return row['cloak_list'][-1]
    else:
        return row['third_party']  # or any other default value you prefer

df['third_party'] = df.apply(update_third_party, axis=1)
df.head()
from publicsuffixlist import PublicSuffixList
psl = PublicSuffixList()
# we only want to see the first party to same third party once
df.loc[:,"third_party"] = df.loc[:,"third_party"].map(lambda tp : psl.privatesuffix(tp))
df.head()
df.to_csv("hars_travel_cloak_clean.csv")
