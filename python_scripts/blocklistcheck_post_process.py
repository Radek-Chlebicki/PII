import pandas as pd

df = pd.read_csv("blocklist_decisions.csv")
print(df.columns)

# print(df.head)

count = df["shouldblock"].value_counts()[True]
print(count)


unwanted = ["60201", "Evaston", "Illinois", "NjAyMD", "RXZhbnN0b2", "SWxsaW5vaX"]
falseThirdParty = ['registerdisney.go.com','www.googleapis.com','login.newscorpaustralia.com','images1.livehindustan.com','www.livehindustan.com','comedycentralstore.com','www.curbed.com'
                    ,'images.livemint.com','www.livemint.com','datahash.livemint.com','sslweb.rcs.it','inapp.rcs.it','map.mp.nbc.com','tribune.signon.trb.com','id.rambler.ru','eulogin.gedi.it',
                    'subs.prd.aws.nymetro.com','api.geekdo.com','oms.expedia.com']


count1 = len(df.loc[(df['shouldblock'] == True) & (~df['string_leaked'].isin(unwanted))  & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where blocked {count1}")

count2 = len(df.loc[(df['shouldblock'] == False) & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where not blocked {count2}")

print("total")
print(count1 + count2)

count = len(df.loc[(df['shouldblock'] == False) & (df['method'] == "get") & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where not blocked get {count}")
count = len(df.loc[(df['shouldblock'] == True) & (df['method'] == "get") & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where blocked get {count}")



count = len(df.loc[(df['shouldblock'] == False) & (df['method'] == "post") & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where not blocked post {count}")
count = len(df.loc[(df['shouldblock'] == True) & (df['method'] == "post") & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where blocked post {count}")


count = len(df.loc[(df['shouldblock'] == False) & (df['method'] == "referer") & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where not blocked referer {count}")
count = len(df.loc[(df['shouldblock'] == True) & (df['method'] == "referer") & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where blocked referer {count}")



count = len(df.loc[(df['shouldblock'] == False) & (df['method'] == "cookie") & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where not blocked cookie {count}")
count = len(df.loc[(df['shouldblock'] == True) & (df['method'] == "cookie") & (~df['string_leaked'].isin(unwanted)) & (~df['third_party'].isin(falseThirdParty)) ])
print(f"number where blocked cookie {count}")



