import pandas as pd
import re
import numpy as np

zuihou = pd.read_excel(r"temp\zuihou.xlsx")
zuihou.head()

zuihou.shape



sj = pd.read_excel(r"city_inefficiency_tree.xlsx")
sj = sj[sj.year.between(2010,2018)]
sj.head()

sj.shape

sj2 = sj[["id","citys"]].drop_duplicates()

sj2

zuihou.shape

zuihou = pd.merge(zuihou,sj2,on=["id"],how = "left").set_index(["id","citys"])

zuihou.head()

col_name1 = [re.findall("class_.+",str(x))[0] for x in zuihou if type(re.search("class_.+",str(x))).__name__ != 'NoneType']

col_name1

zuihou[col_name1] = zuihou[col_name1].applymap(lambda x: re.search(">|<",str(x)).group(0) if type(re.search(">|<",str(x))).__name__ != 'NoneType' else "" )

zuihou

zz = zuihou.iloc[:,:].applymap(lambda x: re.search(">|<",str(x)).group(0) if type(re.search(">|<",str(x))).__name__ != 'NoneType' else "" )

zz

zz.drop(columns=["class","ddf"],inplace=True)

col_name = [re.findall("class_.*",str(x))[0] for x in zz if type(re.search("class_",str(x))).__name__ != 'NoneType']

col_name

zz = zz[col_name]

zz.head()

kind_lt = []
for i in range(zz.shape[0]):
    kind_lt.append("".join(list(zz.iloc[i,:].values)))

kind_lt

zuihou["group"] = kind_lt

zuihou2 = zuihou.sort_values(by="group").reset_index().set_index(["citys","group"]).drop(columns = "id")

zuihou2

zuihou2.replace("",np.nan,inplace=True)

zuihou2.index


gap_provSortMean = pd.DataFrame()
for colN3 in range(0,zuihou2.columns.shape[0],2):
    print(colN3)
    tep = zuihou2.iloc[:,colN3:colN3+2]
    tep2 = tep.groupby([tep.columns[0]]).mean().reset_index()
    gap_provSortMean = pd.concat([gap_provSortMean,tep2],axis=1)


gap_provSortMean

gap_provSortMean.index= [["China mean","China mean"],["",""]]

zuihou3 = pd.concat([zuihou2,gap_provSortMean],axis=0)

zuihou3.index.name  ="id"

zuihou3 = zuihou3.round(3)

zuihou3

for colN4 in range(0,zuihou3.columns.shape[0],2):
    print(colN4)
    zuihou3.iloc[:,colN4] = zuihou3.iloc[:,colN4] + " (" + zuihou3.iloc[:,colN4+1].map(str) + ")"


zuihou3

col_name2 = [re.findall("ddf.*",str(x))[0] for x in zuihou if type(re.search("ddf.*",str(x))).__name__ != 'NoneType']

col_name2

zuihou3.drop(columns=col_name2,inplace=True)

zuihou3

col_name4 = [re.findall("class.*",str(x))[0] for x in zuihou3 if type(re.search("class.*",str(x))).__name__ != 'NoneType']

col_name4

zuihou3.columns = list(map(lambda x :x+"?" + " (ddf)",col_name4))

zuihou3

col_name5 = [re.findall("class_.*",str(x))[0] for x in zuihou3 if type(re.search("class_.*",str(x))).__name__ != 'NoneType']

col_name5

pd.DataFrame(zuihou3.columns).replace("class_","",regex=True).replace("class","split",regex=True).loc[:,0]

zuihou3.columns = pd.DataFrame(zuihou3.columns).replace("class_","",regex=True).replace("class","split",regex=True).loc[:,0]

zuihou3

zuihou3 = zuihou3.replace("split","",regex=True)

zuihou3

zuihou3.to_excel(r"temp\table1.xlsx")

zuihou4 = zuihou3.drop(index = ("China mean","")).reset_index()

zuihou4



daima = pd.read_excel(r".\step2Pre.xlsx")
daima["市"] = daima["市"].replace(r'市',"", regex=True)
daima["省"] = daima["省"].replace(r'市|省',"", regex=True)

daima["省"] = daima["省"].replace({"内蒙古自治区": "内蒙古","广西壮族自治区": "广西", "吉林":"吉林林",
                                    "西藏自治区": "西藏","宁夏回族自治区": "宁夏","新疆维吾尔自治区": "新疆"},)
daima.drop_duplicates(inplace=True)

daima.columns = ["prov_code","provs","city_code","citys"]

zuihou5 = pd.merge(zuihou4,daima,on = "citys",how="left")

zuihou5

zuihou5 = zuihou5[["citys","group","city_code","provs"]]

zuihou5.to_excel(r"temp\fig4Pre.xlsx",index=False)





zuihou7 = zuihou5[["citys","city_code","group","provs"]]

zuihou7

sj = pd.read_excel(r"city_inefficiency_tree.xlsx")
sj = sj[sj.year.between(2010,2018)]

sj2 = sj[["id","citys","year","Y","CO2","K","L","E","fdi","open","tech","human"]]
sj2.head()

zuihou8 = pd.merge(zuihou7,sj2,on = ["citys"],how = "left")

zuihou8

zuihou8.to_excel(r"temp\to_ddf_by_group.xlsx",index=False)