import pandas as pd
import matplotlib.pyplot as plt

params = {
    'figure.figsize': '6, 3'
}
plt.rcParams.update(params)
plt.rc('font',family='Times New Roman')


ene = pd.read_excel(r"fig1Pre.xlsx",sheet_name="E")
ene.head()

ene = ene.set_index("year") * 10**18  / (29270 * 10**6) /10**9 # 千百万吨 tce  （10**9）
ene.head()

ene = ene.reset_index()
ene = ene[ene["year"]>=2010]

# keep if (year>=2010) & (year!=.)
ene.head()


co2 = pd.read_excel(r"fig1Pre.xlsx",sheet_name="CO2")

co2 = co2[co2["year"]>=2010]

co2[co2.columns[1:]] = co2[co2.columns[1:]]/1000
co2.head()

fig, (ax1, ax2) = plt.subplots(1, 2, sharex=False, sharey=False)
ax1.grid(linestyle='dotted')
ax2.grid(linestyle='dotted')
fig.subplots_adjust(right=0.8)

index_male = ene["year"].astype(int)

color = ["#f7dc05","#3d98d3","#ec0b88","#5e35b1","#f9791e","#3dd378"]
label = ['Germany','Japan','Russian Federation','India','US','China']


ax1.plot(index_male, ene["Germany"],label="Germany",color = color[0])
ax1.plot(index_male, ene["Japan"],label="Japan",color = color[1])
ax1.plot(index_male, ene["Russian Federation"],label="Russian",color = color[2])
ax1.plot(index_male, ene["India"],label="India",color = color[3])
ax1.plot(index_male, ene["US"],label="US",color = color[4])
ax1.plot(index_male, ene["China"],label="China",color = color[5])

ax1.set_xticks(index_male)
ax1.set_xticklabels(index_male.values,rotation=60)


index_female = co2["year"].astype(int)
ax2.plot(index_female, co2["Germany"],color = color[0])
ax2.plot(index_female, co2["Japan"],color = color[1])
ax2.plot(index_female, co2["Russian Federation"],color = color[2])
ax2.plot(index_female, co2["India"],color = color[3])
ax2.plot(index_female, co2["US"],color = color[4])
ax2.plot(index_female, co2["China"],color = color[5])
ax2.set_xticks(index_female)
ax2.set_xticklabels(index_female.values,rotation=60)

ax1.set_xlabel('year')
ax2.set_xlabel('year')
ax1.set_ylabel('Primary Energy Consumption ($\mathregular{unit: 10^9 tce}$)')
ax2.set_ylabel('Carbon Dioxide Emissions ($\mathregular{unit: 10^9 tons}$)')

plt.subplots_adjust(wspace=0.45)

fig.legend(ncol=1,loc='lower left', bbox_to_anchor=(2.5,-0.12),bbox_transform=ax1.transAxes)


plt.savefig(r"result\Figure 1 Comparison on Energy consumption and carbon emissions.png", dpi=900, bbox_inches = 'tight',)




import pandas as pd
import re
import numpy as np
import pygal

import os
import subprocess

from sklearn.preprocessing import LabelEncoder



import matplotlib.pyplot as plt



treeregion = pd.read_stata(r"temp\CEEm_CEEregion_CEE_global_by_id_year.dta")
treeregion
treeregion.rename(columns={"enveff_tree":"CEEm" ,"enveff_region":"CEEr", "enveff_global":"CEEG"},inplace= True)

treeregion["TGIm"] = treeregion["CEEm"]- treeregion["CEEG"]
treeregion["TGIr"] = treeregion["CEEr"]- treeregion["CEEG"]

treeregion["CEIm"] = 1 - treeregion["CEEm"]
treeregion["CEIr"] = 1 - treeregion["CEEr"]

treeregion2 = treeregion[["year","city_code", "groupid", "CEEG", "CEEm", "TGIm", "CEEr", "TGIr"]]
treeregion2



treeregion2= treeregion2.groupby(["groupid","year"]).mean()
treeregion2
treeregion2.reset_index()
treeregion2.mean(axis=0)

treeregion3=treeregion2.reset_index().pivot_table(
                    index=["groupid"],   #要保留的主字段
                    columns=["year"] ,                 #拉长的分类变量
                    values=["CEEG","CEEm","TGIm","CEEr","TGIr"]                #拉长的度量值名称
        )
treeregion3

# 去掉两行表头的方法
tgt = treeregion3["TGIm"]
tgt.columns.name=""
# tgt["average"]= tgt.copy().mean(axis=1)
# tgt.loc['National mean']=tgt.mean(axis=0)
tgt.reset_index(inplace=True)
# tgt = pd.DataFrame(["Panel A:CEEG"],columns=["groupid"]).append(tgt,ignore_index= True)

tgt.reset_index(inplace=True)
tgt2 = tgt.copy()
tgt2['index'] = tgt.loc[:,'index'].copy() + 1
tgt = tgt2
tgt2 = tgt.copy()
tgt2.loc[:,'index'] ="group" +  tgt2.loc[:,'index'].copy().map(str)

print(tgt2)

def plot_as_emf(filename, **kwargs):
    inkscape_path = kwargs.get('inkscape', r"D:\Program Files\Inkscape\inkscape.exe")
    filepath = filename
    if filepath is not None:
        path, filename = os.path.split(filepath)
        filename, extension = os.path.splitext(filename)
        svg_filepath = os.path.join(path, filename+'.svg')
        emf_filepath = os.path.join(path, filename+'.emf')
        subprocess.call([inkscape_path, svg_filepath, '--export-emf', emf_filepath])
        # os.remove(svg_filepath)

from pygal.style import Style
custom_style = Style(
                              background= '#FFFFFF',
                              colors= ("#017a4a", "#ffce4e", "#3d98d3", "#ff363c", "#7559a2", "#794924", "#8cdb5e", "#d6d6d6", "#fb8c00"),
                              foreground= '#000000',
                              foreground_strong= '#000000',
                              foreground_subtle= '#828282',

                              plot_background= '#FFFFFF',
                              value_background= 'rgba(229, 229, 229, 1)',

                              font_family='Times New Roman',
                              label_font_family= 'Times New Roman',
                              major_label_font_family= 'Times New Roman',
                              value_font_family= 'Times New Roman',
                              value_label_font_family= 'Times New Roman',
                              tooltip_font_family= 'Times New Roman',
                              title_font_family='Times New Roman',
                              legend_font_family='Times New Roman',
                              label_font_size=14,
                              # major_label_font_size=24,
                              # value_font_size=24,
                              # value_label_font_size=24,
                              # tooltip_font_size=24,
                              # title_font_size=24,
                              # legend_font_size=24,
                              # no_data_font_size=24,

)

radar_chart = pygal.Radar( style=custom_style,width=475,height=400)
# radar_chart.title = 'V8 benchmark results'#图的标题
radar_chart.x_labels = tgt2["index"]    #雷达图中的坐标的标签
print(tgt2["index"],"xxxxxxxxxxxxxxxxx")
radar_chart.y_labels = [0,0.1,0.2,0.3,0.4]    #雷达图中的坐标的标签

radar_chart.add('2010',tgt2[2010],stroke_style={'width': 4, 'dasharray': '24'})#添加数据
radar_chart.add('2011',tgt2[2011],stroke_style={'width': 2, 'dasharray': '12'})#添加数据
radar_chart.add('2012',tgt2[2012],stroke_style={'width': 2, 'dasharray': '13'})#添加数据
radar_chart.add('2013',tgt2[2013],stroke_style={'width': 2, 'dasharray': '14'})#添加数据
radar_chart.add('2014',tgt2[2014],stroke_style={'width': 2, 'dasharray': '15'})#添加数据
radar_chart.add('2015',tgt2[2015],stroke_style={'width': 2, 'dasharray': '16'})#添加数据
radar_chart.add('2016',tgt2[2016],stroke_style={'width': 2, 'dasharray': '17'})#添加数据
radar_chart.add('2017',tgt2[2017],stroke_style={'width': 2, 'dasharray': '18'})#添加数据
radar_chart.add('2018',tgt2[2018],stroke_style={'width': 4,})#添加数据

radar_chart.render()
# radar_chart.render_to_png('result\TG雷达图.png')#保存文件
filename = 'result\Figure 5. Technology gap inefficiency TGIm by group over years.svg'
radar_chart.render_to_file(filename)#保存文件
# plot_as_emf(filename)




import pandas as pd
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt



treeregion = pd.read_stata(r"temp\CEEm_CEEregion_CEE_global_by_id_year.dta")
treeregion
treeregion.rename(columns={"enveff_tree":"CEEm" ,"enveff_region":"CEEr", "enveff_global":"CEEG"},inplace= True)

treeregion["TGIm"] = treeregion["CEEm"]- treeregion["CEEG"]
treeregion["TGIr"] = treeregion["CEEr"]- treeregion["CEEG"]

treeregion["CEIm"] = 1 - treeregion["CEEm"]
treeregion["CEIr"] = 1 - treeregion["CEEr"]


zhongweishu = treeregion[treeregion["year"]==2018][["provs","citys","groupid","CEIm","TGIm"]]
zhongweishu.columns


zhongweishu.loc[(zhongweishu["CEIm"]<zhongweishu["CEIm"].median()) &  (zhongweishu["TGIm"]<zhongweishu["TGIm"].median()),"part"]=1
zhongweishu.loc[(zhongweishu["CEIm"]>=zhongweishu["CEIm"].median()) &  (zhongweishu["TGIm"]<zhongweishu["TGIm"].median()),"part"]=2
zhongweishu.loc[(zhongweishu["CEIm"]<zhongweishu["CEIm"].median()) &  (zhongweishu["TGIm"]>=zhongweishu["TGIm"].median()),"part"]=3
zhongweishu.loc[(zhongweishu["CEIm"]>=zhongweishu["CEIm"].median()) &  (zhongweishu["TGIm"]>=zhongweishu["TGIm"].median()),"part"]=4
# zhongweishu["groupid"] = pd.Categorical(zhongweishu.groupid)

# zhongweishu["groupid2"] = zhongweishu["groupid"].cat.codes

zhongweishu['groupid'] = LabelEncoder().fit_transform(zhongweishu['groupid'])+1

table = zhongweishu[["groupid","part","citys"]].groupby(["groupid","part"]).count().reset_index().pivot(index='groupid', columns='part', values='citys').reset_index()
table["groupid"]= "group" + table["groupid"].map(str)
table.columns=["groupid","I","II","III","IV"]
table.set_index("groupid",inplace=True)
table.fillna(0,inplace=True)
table = table.astype(int)
table
CEITm  = zhongweishu["CEIm"].describe()["50%"]
TGIm  = zhongweishu["TGIm"].describe()["50%"]
TGIm


ss1 =zhongweishu[zhongweishu["groupid"]==1][["provs","citys","TGIm","CEIm"]]
ss2 =zhongweishu[zhongweishu["groupid"]==2][["provs","citys","TGIm","CEIm"]]
ss3 =zhongweishu[zhongweishu["groupid"]==3][["provs","citys","TGIm","CEIm"]]
ss4 =zhongweishu[zhongweishu["groupid"]==4][["provs","citys","TGIm","CEIm"]]
ss5 =zhongweishu[zhongweishu["groupid"]==5][["provs","citys","TGIm","CEIm"]]
ss6 =zhongweishu[zhongweishu["groupid"]==6][["provs","citys","TGIm","CEIm"]]
ss7 =zhongweishu[zhongweishu["groupid"]==7][["provs","citys","TGIm","CEIm"]]
ss8 =zhongweishu[zhongweishu["groupid"]==8][["provs","citys","TGIm","CEIm"]]
ss9 =zhongweishu[zhongweishu["groupid"]==9][["provs","citys","TGIm","CEIm"]]
ss10 =zhongweishu[zhongweishu["groupid"]==10][["provs","citys","TGIm","CEIm"]]


fig, ax = plt.subplots()
ax.grid(linestyle='dotted')
fig.subplots_adjust(right=0.8)
color = ['#E21034','#FB44C3','#F7D046','#FDFF70','#1AF11C','#008000','#82F7DE','#0848EF','#753476','#7A1EEB']
scs1 = ax.scatter(ss1["CEIm"], ss1["TGIm"], label='$\mathregular{group1}$',color=color[0],)    # ①
scs2 = ax.scatter(ss2["CEIm"], ss2["TGIm"], label='$\mathregular{group2}$',color=color[1] )    # ①
scs3 = ax.scatter(ss3["CEIm"], ss3["TGIm"], label='$\mathregular{group3}$',color=color[2])    # ①
scs4 = ax.scatter(ss4["CEIm"], ss4["TGIm"], label='$\mathregular{group4}$',color=color[3])    # ①
scs5 = ax.scatter(ss5["CEIm"], ss5["TGIm"], label='$\mathregular{group5}$',color=color[4])    # ①
scs6 = ax.scatter(ss6["CEIm"], ss6["TGIm"], label='$\mathregular{group6}$',color=color[5])    # ①
scs7 = ax.scatter(ss7["CEIm"], ss7["TGIm"], label='$\mathregular{group7}$',color=color[6])    # ①
scs8 = ax.scatter(ss8["CEIm"], ss8["TGIm"], label='$\mathregular{group8}$',color=color[7])    # ①
scs9 = ax.scatter(ss9["CEIm"], ss9["TGIm"], label='$\mathregular{group9}$',color=color[8])    # ①
scs10 = ax.scatter(ss10["CEIm"], ss10["TGIm"], label='$\mathregular{group10}$',color=color[9])    # ①

# zz = ss9
# for i in range(len(zz["CEIm"])):
#     plt.annotate(zz["provs"].iloc[i]+zz["citys"].iloc[i], xy = (zz["CEIm"].iloc[i], zz["TGIm"].iloc[i]), xytext = (zz["CEIm"].iloc[i], zz["TGIm"].iloc[i]),fontproperties="SimSun") # 这里xy是需要标记的坐标，xytext是对应的标签坐标


liney = ax.axhline(TGIm, color = 'black',linewidth=0.5)    # ①
liney = ax.axvline(CEITm, color='black',linewidth=0.5)    # ①

plt.annotate('I', xy = (-0.03, 0.00), xytext = (-0.03, 0.00))
plt.annotate('II', xy = (0.79, 0.00), xytext = (0.79, 0.00))
plt.annotate('III', xy = (-0.03, 0.52), xytext = (-0.03, 0.52))
plt.annotate('IV', xy = (0.79, 0.52), xytext = (0.79, 0.52))
# ax.set_xticks(cer232["year"])   # ③
# # ax.xaxis.set_major_formatter(ticker.IndexFormatter([0]+cer232["year"].tolist()))    # ④



col_labels = table.columns
row_labels = table.index
table_vals = list(table.values)
row_colors = ['#E21034','#FB44C3','#F7D046','#FDFF70','#1AF11C','#008000','#82F7DE','#0848EF','#753476','#7A1EEB']
my_table = plt.table(cellText=table_vals,colWidths=[0.05]*10,
   rowLabels=row_labels, colLabels=col_labels,
   bbox = [1.15, 0.025, 0.20, 0.7],rowColours=row_colors )


#设置横纵坐标的名称以及对应字体格式
font2 = {'family' : 'Times New Roman',
'weight' : 'normal',
'size'   : 10,
}
plt.xlabel('$\mathregular{CEI^m}$',font2)
plt.ylabel('$\mathregular{TGI^m}$',font2)
# #设置坐标刻度值的大小以及刻度值的字体
# plt.tick_params(labelsize=10)
# # labels = ax.get_xticklabels() + ax.get_yticklabels()
# # [label.set_fontname('Times New Roman') for label in labels]


# for a,b,c in zip(index_male,ss1.values,(ss1/(ss1+ss2)*100).values):
#     plt.text(a, b-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_male,ss2.values,(ss2/(ss1+ss2)*100).values):
#     plt.text(a, b/ (c/100)-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_female,ss3.values,(ss3/(ss3+ss4)*100).values):
#     plt.text(a, b-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_female,ss4.values,(ss4/(ss3+ss4)*100).values):
#     plt.text(a, b/ (c/100)-30, '{:.1f}%'.format(c), ha='center',fontsize= 6)

# ax2=ax.twinx()
# rects2 = ax2.plot(cer232["year"], sss.values , marker = '^', color='khaki',label="ratio",linestyle=':')
# ax2.set_ylabel('The ratio of emission reductions to total emissions')

fig.legend(ncol=1,loc='lower left', bbox_to_anchor=(-0.34,0),bbox_transform=ax.transAxes,borderpad=0.0,handletextpad=0.05)
# plt.show()

plt.savefig(r"result\Figure 6. Carbon emission inefficiency CEIm and technology gap inefficiency TGIm.png", dpi=900, bbox_inches = 'tight')





import pandas as pd
import matplotlib.pyplot as plt



treeregion = pd.read_stata(r"temp\CEEm_CEEregion_CEE_global_by_id_year.dta")
treeregion
treeregion.rename(columns={"enveff_tree":"CEEm" ,"enveff_region":"CEEr", "enveff_global":"CEEG"},inplace= True)

treeregion["TGIm"] = treeregion["CEEm"]- treeregion["CEEG"]
treeregion["TGIr"] = treeregion["CEEr"]- treeregion["CEEG"]

treeregion["CEIm"] = 1 - treeregion["CEEm"]
treeregion["CEIr"] = 1 - treeregion["CEEr"]


treeregion7 = treeregion[["year", "groupid", "CEEG", "CEEm", "TGIm", "CEEr", "TGIr","CO2"]]
treeregion72=treeregion7.copy()
treeregion7=treeregion72.copy()
treeregion7["CER"] = (1-treeregion7["CEEG"]) * treeregion7["CO2"]
treeregion7["CERm"] = (1-treeregion7["CEEm"]) * treeregion7["CO2"]
treeregion7["CERTGm"] = (treeregion7["TGIm"]) * treeregion7["CO2"]
treeregion7["CERr"] = (1-treeregion7["CEEr"]) * treeregion7["CO2"]
treeregion7["CERTGr"] = (treeregion7["TGIr"]) * treeregion7["CO2"]
treeregion7= treeregion7.groupby(["year"]).mean()



sss = treeregion7["CER"]/treeregion7["CO2"] * 100
sss
# 去掉两行表头的方法
cer232 = treeregion7[["CER","CERm","CERTGm","CERr","CERTGr"]]
cer232.columns.name=""
# cer232.loc['National sum']=cer232.sum(axis=0)
cer232.reset_index(inplace=True)
# cer232.rename(columns = {"index":"group"},inplace = True)
cer232



params = {
    'figure.figsize': '6, 4'
}
plt.rcParams.update(params)
plt.rc('font',family='Times New Roman')

ss1 =cer232["CERm"]
ss2 =cer232["CERTGm"]
ss3 =cer232["CERr"]
ss4 =cer232["CERTGr"]

fig, ax = plt.subplots()
ax.grid(linestyle='dotted')

bar_width = 0.42 # 条形宽度
index_male = cer232["year"] - bar_width/2 # 男生条形图的横坐标
index_female = cer232["year"] + bar_width/2  # 女生条形图的横坐标

CERT = ax.bar(index_male, ss1.values,width=bar_width, label='$\mathregular{CER^m}$')    # ①
CERTGI =ax.bar(index_male, ss2.values,width=bar_width, bottom=ss1.values, label='$\mathregular{CERTG^{m}}$')    # ②
CERR =ax.bar(index_female,ss3.values , width=bar_width, label='$\mathregular{CER^{r}}$')
CERRGI =ax.bar(index_female,ss4.values , width=bar_width, bottom=ss3.values,label='$\mathregular{CERTG^{r}}$''')

ax.set_xticks(cer232["year"])   # ③
# ax.xaxis.set_major_formatter(ticker.IndexFormatter([0]+cer232["year"].tolist()))    # ④

font1 = {'family' : 'Times New Roman',
'weight' : 'normal',
'size'   :10,
}

#设置横纵坐标的名称以及对应字体格式
font2 = {'family' : 'Times New Roman',
'weight' : 'normal',
'size'   : 10,
}
plt.xlabel('year',font2)
plt.ylabel('CER',font2)
#设置坐标刻度值的大小以及刻度值的字体
plt.tick_params(labelsize=10)
# labels = ax.get_xticklabels() + ax.get_yticklabels()
# [label.set_fontname('Times New Roman') for label in labels]


for a,b,c in zip(index_male,ss1.values,(ss1/(ss1+ss2)*100).values):
    plt.text(a, b-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
for a,b,c in zip(index_male,ss2.values,(ss2/(ss1+ss2)*100).values):
    plt.text(a, b/ (c/100)-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
for a,b,c in zip(index_female,ss3.values,(ss3/(ss3+ss4)*100).values):
    plt.text(a, b-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
for a,b,c in zip(index_female,ss4.values,(ss4/(ss3+ss4)*100).values):
    plt.text(a, b/ (c/100)-30, '{:.1f}%'.format(c), ha='center',fontsize= 6)

ax2=ax.twinx()
rects2 = ax2.plot(cer232["year"], sss.values , marker = '^', color='khaki',label="ratio",linestyle=':')
ax2.set_ylabel('The ratio of emission reductions to total emissions')

fig.legend(prop=font1,ncol=3,loc='lower left', bbox_to_anchor=(0.0,0),bbox_transform=ax.transAxes)


plt.savefig("result\Figure 8. Carbon reduction potential and its components.png", dpi=900, bbox_inches = 'tight')










import pandas as pd
import warnings
warnings.filterwarnings("ignore")

treeregion = pd.read_stata(r"temp\CEEm_CEEregion_CEE_global_by_id_year.dta")
treeregion
treeregion.rename(columns={"enveff_tree":"CEEm" ,"enveff_region":"CEEr", "enveff_global":"CEEG"},inplace= True)

treeregion["TGIm"] = treeregion["CEEm"]- treeregion["CEEG"]
treeregion["TGIr"] = treeregion["CEEr"]- treeregion["CEEG"]

treeregion["CEIm"] = 1 - treeregion["CEEm"]
treeregion["CEIr"] = 1 - treeregion["CEEr"]

treeregion2 = treeregion[["year","city_code", "groupid", "CEEG", "CEEm", "TGIm", "CEEr", "TGIr"]]
treeregion2



treeregion2= treeregion2.groupby(["groupid","year"]).mean()
treeregion2
treeregion2.reset_index()
treeregion2.mean(axis=0)

treeregion3=treeregion2.reset_index().pivot_table(
                    index=["groupid"],   #要保留的主字段
                    columns=["year"] ,                 #拉长的分类变量
                    values=["CEEG","CEEm","TGIm","CEEr","TGIr"]                #拉长的度量值名称
        )
treeregion3

# 去掉两行表头的方法
ceeg = treeregion3["CEEG"]
ceeg.columns.name=""
ceeg.index="group" + pd.Series(range(1,len(ceeg.index)+1)).map(str)

ceeg2=ceeg.copy()
ceeg=ceeg2.copy()
ceeg["average"]= ceeg.copy().mean(axis=1)
ceeg.loc['National mean']=ceeg.mean(axis=0)
ceeg.reset_index(inplace=True)

ceeg.rename(columns = {"index":"group"},inplace = True)

ceeg = pd.DataFrame(["Panel A:CEEG"],columns=["group"]).append(ceeg,ignore_index= True)

ceeg

# 去掉两行表头的方法
ceet = treeregion3["CEEm"]
ceet.columns.name=""
ceet.index="group" + pd.Series(range(1,len(ceet.index)+1)).map(str)

ceet2=ceet.copy()
ceet=ceet2.copy()
ceet["average"]= ceet.copy().mean(axis=1)
ceet.loc['National mean']=ceet.mean(axis=0)
ceet.reset_index(inplace=True)
ceet.rename(columns = {"index":"group"},inplace = True)
ceet = pd.DataFrame(["Panel B:CEEm"],columns=["group"]).append(ceet,ignore_index= True)

ceet

cee = pd.concat([ceeg,ceet])
cee

cee.to_excel(r"result\Table 3.Results on carbon emission efficiency.xlsx",index=False)





import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

params = {
    'figure.figsize': '6, 4'
}
plt.rcParams.update(params)
plt.rc('font',family='Times New Roman')

lmdi = pd.read_stata(r"temp\lmdi_management_failure.dta")
lmdi = lmdi[lmdi["year"]>2010][["groupid","Dtot","Eff_1","Eff_2","Eff_3"]]
lmdi["groupid2"]= "group" + lmdi["groupid"].map(int).map(str)
lmdi.columns=["groupid","CER","CEI","CI","PS","groupid2"]
lmdi.set_index("groupid2",inplace=True)
# table.fillna(0,inplace=True)
lmdi = lmdi.round(2)
lmdi

ss1 = lmdi["CEI"]
ss2 = lmdi["CI"]
ss3 = lmdi["PS"]
# ss4 =lmdi["Eff_4"]

data = np.array([ss1, ss2, ss3])
data_shape = np.shape(data)


# Take negative and positive data apart and cumulate
def get_cumulated_array(data, **kwargs):
    cum = data.clip(**kwargs)
    cum = np.cumsum(cum, axis=0)
    d = np.zeros(np.shape(data))
    d[1:] = cum[:-1]
    return d


cumulated_data = get_cumulated_array(data, min=0)
cumulated_data_neg = get_cumulated_array(data, max=0)

# Re-merge negative and positive data.
row_mask = (data < 0)
cumulated_data[row_mask] = cumulated_data_neg[row_mask]
data_stack = cumulated_data

fig, ax = plt.subplots()
ax.grid(linestyle='dotted')
fig.subplots_adjust(right=0.65)

index_male = lmdi["groupid"]
label = ['$\mathregular{CEI^m}$', '$\mathregular{CI^m}$', '$\mathregular{PS^m}$']
color = ["#FF9900", "#4674D1", "#DC3912"]
for i in np.arange(0, data_shape[0]):
    ax.bar(index_male, data[i], bottom=data_stack[i], label=label[i], color=color[i])

xzhou = "group" + (lmdi["groupid"]).map(int).map(str)
ax.set_xticks(lmdi["groupid"])  # ③
ax.set_xticklabels(xzhou.values, rotation=45)
plt.xlabel('group')
plt.ylabel('Changes in CO2 reduction potential')
plt.tick_params(labelsize=10)

rects2 = ax.plot(index_male, lmdi["CER"].values, marker='^', color='black', label="$\mathregular{CER^m}$",
                 linestyle=':')

col_labels = ['$\mathregular{CER^m}$', '$\mathregular{CEI^m}$', '$\mathregular{CI^m}$', '$\mathregular{PS^m}$']
row_labels = lmdi.index
table_vals = list(lmdi[lmdi.columns[1:]].values)
row_colors = ['#E21034', '#FB44C3', '#F7D046', '#FDFF70', '#1AF11C', '#008000', '#82F7DE', '#0848EF', '#753476',
              '#7A1EEB']
my_table = plt.table(cellText=table_vals, colWidths=[0.2] * 10,
                     rowLabels=row_labels, colLabels=col_labels, fontsize=60,
                     bbox=[1.11, 0.0, 0.5, 1], rowColours=row_colors)

fig.legend(ncol=2, loc='lower left', bbox_to_anchor=(0, 0), bbox_transform=ax.transAxes)

# for a,b,c in zip(index_male,ss1.values,(ss1/(ss1+ss2)*100).values):
#     plt.text(a, b-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_male,ss2.values,(ss2/(ss1+ss2)*100).values):
#     plt.text(a, b/ (c/100)-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_female,ss3.values,(ss3/(ss3+ss4)*100).values):
#     plt.text(a, b-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_female,ss4.values,(ss4/(ss3+ss4)*100).values):
#     plt.text(a, b/ (c/100)-30, '{:.1f}%'.format(c), ha='center',fontsize= 6)


plt.savefig("result\Figure 9. CO2 emission reduction potential changes caused by managerial failure.png", dpi=900, bbox_inches='tight')



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

params = {
    'figure.figsize': '6, 4'
}
plt.rcParams.update(params)
plt.rc('font',family='Times New Roman')

lmdi2 = pd.read_stata(r"temp\lmdi_technological_gap.dta")
lmdi2 = lmdi2[lmdi2["year"]>2010][["groupid","Dtot","Eff_1","Eff_2","Eff_3"]]
lmdi2["groupid2"]= "group" + lmdi2["groupid"].map(int).map(str)
lmdi2.columns=["groupid","CER","CEI","CI","PS","groupid2"]
lmdi2.set_index("groupid2",inplace=True)
# table.fillna(0,inplace=True)
lmdi2 = lmdi2.round(2)
lmdi2

ss1 = lmdi2["CEI"]
ss2 = lmdi2["CI"]
ss3 = lmdi2["PS"]
# ss4 =lmdi2["Eff_4"]

data = np.array([ss1, ss2, ss3])
data_shape = np.shape(data)


# Take negative and positive data apart and cumulate
def get_cumulated_array(data, **kwargs):
    cum = data.clip(**kwargs)
    cum = np.cumsum(cum, axis=0)
    d = np.zeros(np.shape(data))
    d[1:] = cum[:-1]
    return d


cumulated_data = get_cumulated_array(data, min=0)
cumulated_data_neg = get_cumulated_array(data, max=0)

# Re-merge negative and positive data.
row_mask = (data < 0)
cumulated_data[row_mask] = cumulated_data_neg[row_mask]
data_stack = cumulated_data

fig, ax = plt.subplots()
ax.grid(linestyle='dotted')
fig.subplots_adjust(right=0.65)

index_male = lmdi2["groupid"]
label = ['$\mathregular{CEITGI^m}$', '$\mathregular{CITGI^m}$', '$\mathregular{PSTGI^m}$']
color = ["#FF9900", "#4674D1", "#DC3912"]

for i in np.arange(0, data_shape[0]):
    ax.bar(index_male, data[i], bottom=data_stack[i], label=label[i], color=color[i])

xzhou = "group" + (lmdi2["groupid"]).map(int).map(str)
ax.set_xticks(lmdi2["groupid"])  # ③
ax.set_xticklabels(xzhou.values, rotation=45)
plt.xlabel('group')
plt.ylabel('Changes in CO2 reduction potential')
plt.tick_params(labelsize=10)

rects2 = ax.plot(index_male, lmdi2["CER"].values, marker='^', color='black', label="$\mathregular{CERTGI^m}$",
                 linestyle=':')

col_labels = ['$\mathregular{CERTGI^m}$', '$\mathregular{CEITGI^m}$', '$\mathregular{CITGI^m}$',
              '$\mathregular{PSTGI^m}$']
row_labels = lmdi2.index
table_vals = list(lmdi2[lmdi2.columns[1:]].values)

row_colors = ['#E21034', '#FB44C3', '#F7D046', '#FDFF70', '#1AF11C', '#008000', '#82F7DE', '#0848EF', '#753476',
              '#7A1EEB']
my_table = plt.table(cellText=table_vals, colWidths=[0.25] * 10,
                     rowLabels=row_labels, colLabels=col_labels, fontsize=60,
                     bbox=[1.11, 0.0, 0.6, 1], rowColours=row_colors)

fig.legend(ncol=2, loc='lower left', bbox_to_anchor=(-0.0, 0), bbox_transform=ax.transAxes)

# for a,b,c in zip(index_male,ss1.values,(ss1/(ss1+ss2)*100).values):
#     plt.text(a, b-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_male,ss2.values,(ss2/(ss1+ss2)*100).values):
#     plt.text(a, b/ (c/100)-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_female,ss3.values,(ss3/(ss3+ss4)*100).values):
#     plt.text(a, b-60, '{:.1f}%'.format(c), ha='center',fontsize=6)
# for a,b,c in zip(index_female,ss4.values,(ss4/(ss3+ss4)*100).values):
#     plt.text(a, b/ (c/100)-30, '{:.1f}%'.format(c), ha='center',fontsize= 6)


plt.savefig("result\Figure 10. CO2 emission reduction potential changes caused by technology gap.png", dpi=900, bbox_inches='tight')

















