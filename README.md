详细介绍参见我的[博客](https://blog.huaxiangshan.com/zh-cn/posts/statagis/)

估计每个经济学学习者都向往过掌握全套统计语言的自己——Python机器学习与爬虫，Stata计量回归，R绘图和文本分析，Gis遥感与着色，Matlab解均衡模型和仿真实验。不过人的精力终究还是有限的，个人决定先尝试用Stata实现其他语言的优势项目，例如stata:[爬虫学习](https://blog.huaxiangshan.com/zh-cn/posts/pachong/)。

今天这里记录的是用Stata画Gis着色图的过程。

## 获取地图文件

`ESRI Shapefile`文件是由[美国环境系统研究所](https://www.esri.com/en-us/home)开发的空间地理数据。里面同时储存空间位置和特征数据。其基本文件主要为：

- **主文件 (.shp)：** 存储几何要素的的空间信息，也就是 XY 坐标。
- **索引文件 (.shx)：** 存储有关 .shp 存储的索引信息。它记录了在 .shp 中，空间数据是如何存储的，XY 坐标的输入点在哪里，有多少 XY 坐标对等信息。
- **表文件 (.dbf)：** 存储地理数据的属性信息的 dBase 表。

这里介绍写我找到的一些数据源：

- [大饼的博客](http://gaohr.win/site/blogs/2017/2017-04-18-GIS-basic-data-of-China.html)

- [全国地理信息资源目录服务系统](https://www.webmap.cn/main.do?method=index)

- [GADM data](https://gadm.org/data.html)：国际地图很全。

- [github随手找到的中国地图数据](https://github.com/GaryBikini/ChinaAdminDivisonSHP)

- [Rstata资料](https://github.com/Wsf921109/stata-prov-map?tab=readme-ov-file)：中国地图省级分区。国内买课世界一流，个人觉得stata专题做得最好的是“连享会"和"Rstata"。即便我是坚定的~~白嫖~~开源主义，也经常看他们的科普文章学习stata。此处是有好心人上传了Rstata相关的数据库。

- [中科院地资所](https://www.resdc.cn/Default.aspx)：或许是国内的半官方？

  ![中科院地资所](/img/image-20240323132924391.png)

如果还找不到自己想要的，可以使用阿里云地图来生成地图文件。

进入[阿里云地图](http://datav.aliyun.com/portal/school/atlas/area_selector)，点击文件下载（推荐其他下载，下载后得到`.json`文件）。

下载好后进入[转化器](https://mapshaper.org/)转化。点击`Select`，上传`.json`文件，然后点击`export`导出转化后的文件。

>似乎是因为数据编码或者加密，有时候转阿里云地图化的文件无法被stata读取。
>
>此时使用`spshape2dta`转化

## stataGis初步操作

### 下载相关命令

包含`主文件 (.shp)`和`表文件 (.dbf)`即可。

提前在stata下载相关命令。

```sql
ssc install shp2dta, replace   //文件转化命令
ssc install mif2dta, replace  //文件转化命令
ssc install spmap, replace  //GIS画图命令
```

### 转译和编译乱码

使用B站一位用户用GIS画的文件：[2019中国地图-审图号GS(2019)1822号](https://pan.baidu.com/s/1lybhxKO3EL5JKATULS-0CA?pwd=zkks)

这里个人使用的举例数据是：[北大数字普惠金融指数2011_2020](https://idf.pku.edu.cn/yjcg/zsbg/513800.htm)

这里要转译的有两个文件，中国地图文件`市`和九段线文件`九段线`

```sql
clear 
cd F:\桌面\GIS_sum\2019中国地图审图号\例子
//设置工作环境文件夹，因为gis一些命令参数使用相对路径更好用些

import excel "F:\桌面\GIS_sum\2019中国地图审图号\例子\北大数字普惠金融指数2011_2020.xlsx", sheet("Sheet1") firstrow
keep if year == 2020
rename pref_name_year18 ct_name
save d2020data ,replace
//载入数据

spshape2dta 市
spshape2dta 九段线
//这里因为无法用shp2dta转化所以使用spshape2dta

clear 
cd F:\桌面\GIS_sum\2019中国地图审图号\例子
unicode encoding set gb18030
unicode analyze 市.dta 
unicode translate 市.dta, invalid 
//部分中文乱码重新编译
//一次性命令，若要重新使用需要删掉目录生成的编码文件bak.stunicode
```

若文件无法被转化，例如阿里云的地图，似乎gis做的地图也无法被`shp2dta`转化。这里就是使用的`spshape2dta`转化。

> 两个命令除了这一点外[区别不大](https://www.cda.cn/discuss/post/details/61cd24316276b453ec6f9bc2)。`spshape2dta`命令缺点是不能自定义名字，后面直接跟文件名即可，会自动生成两个需要的文件。标签文件为`.dta`,轮廓文件为`_shp.dta`

### 匹配数据和标签文件

```sql
use 市.dta
rename __ ct_name
save 市.dta ,replace

use d2020data
merge 1:1 ct_name using 市.dta
drop _merge
gen ID =_ID
save city_data2020,replace
```

### 绘图命令

开始绘图，基本绘图命令如下

```sql
grmap digitization_level using 市_shp.dta  , ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(-1 0 190 200 280 300 350) ///
	fcolor(gray "224 242 241" "178 223 219" "128 203 196" "77 182 172" "38 166 154") ///
	leg(order(2 "无数据" 3 "0~190" 4 "190~200" 5 "200~280" 6 "280~300" 7 "300~350")) ///
		graphr(margin(medium)) ///
			line(data(九段线_shp.dta)) ///
	ti("2020 年数字普惠金融指数") ///
	subti("二级标题") ///
	caption("数据来源：北大数字普惠金融指数", size(*0.8))
```

![就画图命令而言，spmap和grmap似乎没有区别](/img/image-20240324105155970.png)

### 参数解释

以下参数解释由GPT3.5给出，个人进行简单补充。

- `grmap type`：指定图形类型为地图。

- `using chinaprov40_coord.dta`：指定地图数据文件，包含省级行政区划的坐标信息。

- `id(ID)`：指定地图数据中的唯一标识符变量。通过标识对应地图坐标和标签和数据。

- `osize(vvthin ...)` 和 `ocolor(white ...)`：设置地图边界线的粗细和颜色。

- `vvthin` 是 Stata 中一种预定义的线条样式，它表示非常细的线条。在绘制地图时，可以使用不同的线条粗细来区分不同的地理要素或边界。

  > 从细到粗排列为：vvthin、vthin、thin、medium、thick、vthick、vvthick。

- `clmethod(custom)` 和 `clbreaks(0 1 2 3 4 5)`：自定义分类方法和分类间隔。这里对应的是省级分类，直辖市，省，特别行政区...

- `fcolor(...)`：指定不同分类的填充颜色。

  > 例子中采用的是三元色定义表示，可以用PPT的颜色自定义查看颜色标识。

  ![三元色定义](/img/image-20240323162244343.png)

- `leg(...)`：设置图例的顺序和标签。

- `graphr(margin(medium))`：设置图形的边距。

- `line(data(chinaprov40_line_coord.dta) by(group) ...)`：绘制地图边界线，指定边界线数据文件和颜色等属性。这里用的是九段线文件。

- `polygon(data(polygon) fcolor(black) ...)`：绘制地图多边形，指定填充颜色和线条粗细等属性。这里是图例和指南针。

- `label(data(chinaprov40_label) ...)`：标注地图上的标签，指定标签数据文件和标签文本等属性。`label(ename)`是英文，`label(cnname)`是中文。

- `ti("一级标题: 2019 年中国省级行政区划")`：设置主标题。

- `subti("二级标题")`：设置副标题。

- `caption("使用 Stata 绘制中国省级地图", size(*0.8))`：设置图形的说明。

## 处理流程图

> 地图线条数据（非必要）：例如山川、河流、山脉、九段线、秦岭淮河、胡焕庸线的线条。

{{< mermaid >}}

graph TD;

0(获取地图文件 )==>1(地图主文件.shp );

0(获取地图文件 )==>11(线条主文件.shp );

0(获取地图文件 )==> 3(表文件 .dbf);

  1(地图主文件.shp )==转译==>2(地图轮廓数据);

11(线条主文件.shp )==转译==>9(地图线条数据);

  3(表文件 .dbf)==转译==>4(标签文件);
  5(数据分析文件)-->6(匹配文件);
   4(标签数据)-->6(匹配文件);
   6(匹配文件)--id标识-->7(画图);
    2(地图轮廓数据)--id标识-->7(画图);
9(地图线条数据)-.id标识.->7(画图);

{{< /mermaid >}}

## 国内省级

> 来自Rstata。可以从[github仓库](https://github.com/Wsf921109/stata-prov-map)下载学习材料——GIS地图省级面板和相关数据。

{{< bilibili BV12L411J7Vt>}}

{{< admonition tip "文件简介" false >}}

地图轮廓数据：

`chinaprov40_db.dta`

`chinaprov40_coord.dta`

线条数据：例如九段线，胡焕庸线等

`chinaprov40_line_db.dta`

`chinaprov40_line_coord.dta`

标签位置数据

`chinaprov40_label.dta`

绘画指北针和比例尺

`polygon.dta`

{{< /admonition >}}

### 正式绘图

```sql
cd /Users/ac/Documents/系列课程/使用Stata绘制中国省级地图（版本4）/
* 离散变量的绘制
use chinaprov40_db.dta, clear 
encode 类型, gen(type)
codebook type

*如果gramp命令没激活，输入grmap, activate命令即可

grmap type using chinaprov40_coord.dta, ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(0 1 2 3 4 5) ///
	fcolor("254 212 57" "253 116 70" "138 145 151" "213 228 162" "210 175 129") ///
	leg(order(2 "不统计" 3 "特别行政区" 4 "直辖市" 5 "省" 6 "自治区" 11 "秦岭-淮河线" 14 "胡焕庸线")) ///
	graphr(margin(medium)) ///
	line(data(chinaprov40_line_coord.dta) by(group) size(vvthin *1 *0.5 *1.2 *0.5 *0.5 *1.2) pattern(solid ...) ///
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  "24 188 156" /// 秦岭淮河线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  "227 26 28" /// 胡焕庸线颜色
			  )) ///
	polygon(data(polygon) fcolor(black) ///
		osize(vvthin)) ///
	label(data(chinaprov40_label) x(X) y(Y) label(cname) length(20) size(*0.8)) ///
	ti("一级标题: 2019 年中国省级行政区划") ///
	subti("二级标题") ///
	caption("使用 Stata 绘制中国省级地图", size(*0.8))
gr export pic1.png, replace width(1200)

* 英文版本
grmap type using chinaprov40_coord.dta, ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(0 1 2 3 4 5) ///
	fcolor("254 212 57" "253 116 70" "138 145 151" "213 228 162" "210 175 129") ///
	leg(order(2 "Not within the scope of statistics" 3 "Special administrative region" 4 "Municipality directly under" "the Central Government" 5 "Province" 6 "Autonomous Region" 11 "Qinling Huaihe River Line" 14 "Hu Huanyong line")) ///
	graphr(margin(medium)) ///
	line(data(chinaprov40_line_coord.dta) by(group) size(vvthin *1 *0.5 *1.2 *0.5 *0.5 *1.2) pattern(solid ...) ///
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  "24 188 156" /// 秦岭淮河线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  "227 26 28" /// 胡焕庸线颜色
			  )) ///
	polygon(data(polygon) fcolor(black) ///
		osize(vvthin)) ///
	label(data(chinaprov40_label) x(X) y(Y) label(ename) length(20) size(*0.6)) ///
	ti("title1: China’s provincial administrative divisions in 2019") ///
	subti("title2") ///
	caption("Use Stata to draw provincial maps of China", size(*0.8))
gr export pic2.png, replace width(1200)


```

![使用 Stata 绘制 2019 年中国省级行政区划](/img/image-20240323160005688.png)

### 其他例子

```sql
* 绘图示例：
* 1. 2020 年中国各省市地区生产总值
import delimited using "2020年中国各省市地区生产总值.csv", clear encoding(utf8)
gen prov = substr(省份, 1, 6)
save 2020年中国各省市地区生产总值, replace 

use chinaprov40_db.dta, clear 
gen prov = substr(省, 1, 6)
merge 1:1 prov using 2020年中国各省市地区生产总值
replace 地区生产总值 = -1 if missing(地区生产总值)
grmap 地区生产总值 using chinaprov40_coord.dta, ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(-1 0 20000 40000 60000 80000 120000) ///
	fcolor(gray "224 242 241" "178 223 219" "128 203 196" "77 182 172" "38 166 154") ///
	leg(order(2 "无数据" 3 "< 2 万亿元" 4 "2～4 万亿元" 5 "4～6 万亿元" 6 "6～8 万亿元" 7 "> 8 万亿元")) ///
	graphr(margin(medium)) ///
	line(data(chinaprov40_line_coord.dta) ///
		/// 去除秦岭淮河线(4)、胡焕庸线(7)
		select(keep if inlist(group, 1, 2, 3, 5, 6)) ///
		by(group) size(vvthin *1 *0.5 *0.5 *0.5) ///
		pattern(solid ...) /// 实线
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  )) ///
	polygon(data(polygon) fcolor(black) ///
		osize(vvthin)) ///
	label(data(chinaprov40_label) x(X) y(Y) label(cname) length(20) size(*0.8)) ///
	ti("2020 年中国各省市地区生产总值") ///
	subti("二级标题") ///
	caption("数据来源：各地统计局", size(*0.8))
gr export pic3.png, replace width(1200)

* 2013 年中国工企业分布及距离秦岭淮河的距离
* 转换坐标系
* 转换方式一：https://czxb.shinyapps.io/crs-trans/
* 注意事项，上传的 csv 文件应该包含数值型的 lon 和 lat 变量，观测值上限大概是 10 万个，不可多人同时使用。
use gq2013sample, clear 
keep 经度 纬度
ren 经度 lon
ren 纬度 lat
export delimited using "待转换.csv", replace 

* 转换方式二：使用附件中的 R 脚本转换

* 处理转换后的数据
import delimited using "转换后的数据.csv", clear 
gen id = _n
save 转换后的数据, replace 

use gq2013sample, clear 
gen id = _n
merge 1:1 id using 转换后的数据
drop _m id *度
encode 北方或南方, gen(north)
save pointdata, replace 

use chinaprov40_db.dta, clear
spmap using chinaprov40_coord.dta, id(ID) ///
	ocolor("black" ...) osize(vvthin ...) ///
    line(data(chinaprov40_line_coord.dta) ///
		/// 胡焕庸线（7）
		select(keep if inlist(group, 1, 2, 3, 4, 5, 6)) ///
		by(group) size(vvthin *1 *0.5 *1.5 *0.5 *0.5) ///
		pattern(solid ...) ///
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  "0 85 170" /// 秦岭淮河线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  )) ///
	polygon(data(polygon) fcolor(black) ///
		osize(vvthin)) ///
	label(data(chinaprov40_label) x(X) y(Y) label(cname) length(20) size(*0.8)) ///
    point(data(pointdata) by(north) ///
    	fcolor("227 26 28%30" "24 188 156%30") ///
        x(x) y(y) ///
        proportional(与秦岭淮河线的距离) ///
        size(*0.1) legenda(on)) ///
    leg(order(7 "秦岭-淮河线" 10 "北方工企业" 11 "南方工企业")) ///
    ti("2013 年中国工业企业与秦岭-淮河线的距离", color(black)) /// 
    subti("二级标题") ///
    graphr(margin(medium)) ///
    caption("数据来源：2013 年中国工业企业数据库，使用高德地图地理编码接口解析经纬度", size(*0.8))
gr export pic4.png, replace width(1200)

* 2019 年中国各省地区生产总值 & 产业结构
use 各省历年GDP, clear 
drop if 省份 == "中国"

replace 地区生产总值_亿元 = 地区生产总值_亿元 / 1000
merge m:m 省代码 using chinaprov40_db.dta
replace 地区生产总值_亿元 = -1 if missing(年份)
grmap 地区生产总值_亿元 if 年份 == 2019 | missing(年份) ///
	using chinaprov40_coord.dta, id(ID) ///
	clmethod(custom) clbreaks(-1 0 40 60 80 100 120) /// 
	fcolor("gray" "237 248 233" "199 233 192" "161 217 155" "116 196 118" "49 163 84") ///
	ocolor("gray" ...) ///
	ti("2019 年中国各省地区生产总值 & 产业结构", size(*1.1)) ///
	subtitle("数据来源：CSMAR经济金融数据库") ///
	graphr(margin(medium)) ///
	osize(vvthin ...) ///
	legend(size(*1.1) ///
		order(2 "无数据" 3 "< 40千亿" ///
			4 "40～60千亿" 5 "60～80千亿" ///
			6 "80～100千亿" 7 "> 100千亿" ///
			14 "第一产业" 15 "第二产业" 16 "第三产业")) ///
	caption("二级标题", size(*0.8)) ///
	line(data(chinaprov40_line_coord.dta) ///
		/// 去除秦岭淮河线(4) 胡焕庸线（7）
		select(keep if inlist(group, 1, 2, 3, 5, 6)) ///
		by(group) size(vvthin *1 *0.5 *0.5 *0.5) ///
		pattern(solid ...) ///
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  )) ///
	polygon(data(polygon) fcolor(black) ///
		osize(vvthin)) ///
	label(data(chinaprov40_label) x(X) y(Y) label(cname) length(20) size(*0.8)) ///
	diagram(data(piedata) x(X) y(Y) v(第一产业占GDP比重_百分比 第二产业占GDP比重_百分比 第三产业占GDP比重_百分比) ///
		type(pie) legenda(on) os(vvthin) ///
			size(1.5) fc("102 194 165" "252 141 98" "229 196 148") ///
			oc("102 194 165" "252 141 98" "229 196 148"))

gr export "pic5.png", replace width(1200)

grmap 地区生产总值_亿元 if 年份 == 2019 | missing(年份) ///
	using chinaprov40_coord.dta, id(ID) ///
	clmethod(custom) clbreaks(-1 0 40 60 80 100 120) /// 
	fcolor("gray" "237 248 233" "199 233 192" "161 217 155" "116 196 118" "49 163 84") ///
	ocolor("gray" ...) ///
	ti("2019 年中国各省地区生产总值 & 第一产业比重", size(*1.1)) ///
	subtitle("数据来源：CSMAR经济金融数据库") ///
	graphr(margin(medium)) ///
	osize(vvthin ...) ///
	legend(size(*1.1) ///
		order(2 "无数据" 3 "< 40千亿" ///
			4 "40～60千亿" 5 "60～80千亿" ///
			6 "80～100千亿" 7 "> 100千亿" ///
			15 "第一产业比重")) ///
	caption("二级标题", size(*0.8)) ///
	line(data(chinaprov40_line_coord.dta) ///
		/// 去除秦岭淮河线(4) 胡焕庸线（7）
		select(keep if inlist(group, 1, 2, 3, 5, 6)) ///
		by(group) size(vvthin *1 *0.5 *0.5 *0.5) ///
		pattern(solid ...) ///
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  )) ///
	polygon(data(polygon) fcolor(black) ///
		osize(vvthin)) ///
	diagram(data(piedata) x(X) y(Y) v(第一产业占GDP比重_百分比) ///
		type(frect) legenda(on) os(vvthin) ///
			size(1.5) fc("252 141 98") ///
			oc("252 141 98") refsize(none))
gr export "pic6.png", replace width(1200)

* 各省人口密度
use 中国人口空间分布省级面板数据集.dta, clear 
ren 省份 省
merge m:1 省 using chinaprov40_db.dta
keep if 年份 == 2015 | missing(年份)
replace 均值 = -1 if missing(均值)
grmap 均值 using chinaprov40_coord.dta, ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(-1 0 100 1000 2000 3000 4000) ///
	fcolor(gray "224 242 241" "178 223 219" "128 203 196" "77 182 172" "38 166 154") ///
	leg(order(2 "无数据" 3 "< 100 人/平方公里" 4 "100～1000 人/平方公里" 5 "1000～2000 人/平方公里" 6 "2000～3000 人/平方公里" 7 "> 3000 人/平方公里" 14 "胡焕庸线")) ///
	graphr(margin(medium)) ///
	line(data(chinaprov40_line_coord.dta) ///
		/// 去除秦岭淮河线(4)
		select(keep if inlist(group, 1, 2, 3, 5, 6, 7)) ///
		by(group) size(vvthin *1 *0.5 *0.5 *0.5 *1.2) ///
		pattern(solid ...) ///
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  "227 26 28" /// 胡焕庸线颜色
			  )) ///
	polygon(data(polygon) fcolor(black) ///
		osize(vvthin)) ///
	label(data(chinaprov40_label) x(X) y(Y) label(cname) length(20) size(*0.8)) ///
	ti("2015 年中国各省平均人口密度") ///
	subti("二级标题") ///
	caption("数据来源：中国科学院资源环境科学与数据中心", size(*0.8))
gr export pic7.png, replace width(1200)
```

### 调节指南针和图例

通过识别相应数据的标识，更改坐标数实现更改效果。

```sql
* 移动指北针的位置到右上方
use chinaprov40_line_db.dta, clear
* 指北针对应的 ID 是 40 和 41
use chinaprov40_line_coord.dta, clear
replace _X = _X + 3000000 if inlist(_ID, 40, 41)
replace _Y = _Y + 4000000 if inlist(_ID, 40, 41)
save chinaprov40_line_coord2.dta, replace 

use polygon, clear
replace _X = _X + 3000000 if _ID == 38
replace _Y = _Y + 4000000 if _ID == 38
save polygon2, replace

use chinaprov40_label, clear
replace X = X + 3000000 if cname == "N"
replace Y = Y + 4000000 if cname == "N"
save chinaprov40_label2, replace 

use chinaprov40_db.dta, clear 
encode 类型, gen(type)
grmap type using chinaprov40_coord.dta, ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(0 1 2 3 4 5) ///
	fcolor("254 212 57" "253 116 70" "138 145 151" "213 228 162" "210 175 129") ///
	leg(order(2 "不统计" 3 "特别行政区" 4 "直辖市" 5 "省" 6 "自治区" 11 "秦岭-淮河线" 14 "胡焕庸线")) ///
	graphr(margin(medium)) ///
	line(data(chinaprov40_line_coord2.dta) by(group) size(vvthin *1 *0.5 *1.2 *0.5 *0.5 *1.2) pattern(solid ...) ///
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  "24 188 156" /// 秦岭淮河线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  "227 26 28" /// 胡焕庸线颜色
			  )) ///
	polygon(data(polygon2) fcolor(black) ///
		osize(vvthin)) ///
	label(data(chinaprov40_label2) x(X) y(Y) label(cname) length(20) size(*0.8)) ///
	ti("使用 Stata 绘制 2019 年中国省级行政区划") ///
	subti("二级标题") ///
	caption("版本：使用 Stata 绘制中国省级地图数据包 4.0", size(*0.8))
gr export pic8.png, replace width(1200)

* 调节比例尺的位置（微微上移）
use chinaprov40_line_db.dta, clear
* 比例尺对应的 ID 是 42 和 43
use chinaprov40_line_coord2.dta, clear
replace _Y = _Y + 200000 if inlist(_ID, 42, 43)
save chinaprov40_line_coord3.dta, replace 

use polygon2, clear
replace _Y = _Y + 200000 if _ID == 39
save polygon3, replace

use chinaprov40_label2, clear
replace Y = Y + 200000 if cname == "1000km"
save chinaprov40_label3, replace 

use chinaprov40_db.dta, clear 
encode 类型, gen(type)
grmap type using chinaprov40_coord.dta, ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(0 1 2 3 4 5) ///
	fcolor("254 212 57" "253 116 70" "138 145 151" "213 228 162" "210 175 129") ///
	leg(order(2 "不统计" 3 "特别行政区" 4 "直辖市" 5 "省" 6 "自治区" 11 "秦岭-淮河线" 14 "胡焕庸线")) ///
	graphr(margin(medium)) ///
	line(data(chinaprov40_line_coord3.dta) by(group) size(vvthin *1 *0.5 *1.2 *0.5 *0.5 *1.2) pattern(solid ...) ///
		color(white /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  "24 188 156" /// 秦岭淮河线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  "227 26 28" /// 胡焕庸线颜色
			  )) ///
	polygon(data(polygon3) fcolor(black) ///
		osize(vvthin)) ///
	label(data(chinaprov40_label3) x(X) y(Y) label(cname) length(20) size(*0.8)) ///
	ti("使用 Stata 绘制 2019 年中国省级行政区划") ///
	subti("二级标题") ///
	caption("版本：使用 Stata 绘制中国省级地图数据包 4.0", size(*0.8))
gr export pic9.png, replace width(1200)
```

## 国内市级

参考[Stata学习：如何绘制省级市级填色地图十段线版？](https://zhuanlan.zhihu.com/p/591146315)

![Using machine learning to model technological heterogeneity in carbon  emission efficiency evaluation: The case of China’s cities ](/img/1-s2.0-S0140988322003826-gr2.jpg)

扒了下论文数据源

## 国内县级

同上，略

## geoplot命令

和`spmap`和`grmap`相比命令更加简洁，定义功能更多，[Ben Jann (University of Bern)](https://www.stata.com/meeting/uk23/slides/UK23_Jann.pdf)

[数据源](https://github.com/benjann/geoplot)

[推荐教程](https://medium.com/the-stata-guide/maps-in-stata-iii-geoplot-a764cf42688a)

### 下载相关命令

```sql
clear
ssc install geoplot, replace
ssc install palettes, replace
ssc install colrspace, replace
ssc install moremata, replace
```

### 载入数据

```sql
cd F:\桌面\GIS_sum\geoplot

local url http://fmwww.bc.edu/repec/bocode/i/
geoframe create regions  `url'Italy-RegionsData.dta, id(id) coord(xcoord ycoord) ///
shpfile(Italy-RegionsCoordinates.dta)
geoframe create country  `url'Italy-OutlineCoordinates.dta
geoframe create capitals `url'Italy-Capitals.dta, coord(xcoord ycoord)
geoframe create lakes    `url'Italy-Lakes.dta, feature(water)
geoframe create rivers   `url'Italy-Rivers.dta, feature(water)
```

含义解释：

> geoframe create 调用名字  地图标签文件和, id(独特标识) coord(经度 纬度) ///
> shpfile(地图轮廓文件)
>
> 每一个宏定义代表一个图层。
>
> 通过这种宏定义，下次只用调用名字就可以画图，省时省力。

### 画图

#### 基本命令

命令优势在于使用简单的括号就满足了图层叠加

```
geoplot (area regions fortell, label("@lb-@ub (N=@n)")) (line regions)
```

> - `area`表示这里是画区域图，使用regions宏名字的地图轮廓，绘图变量是fortell
> - `label`：在地图中，这些变量将被替换为实际的数值。例如，如果某个区域的下限值为 `20`，上限值为 `50`，并且该区域包含 `100` 个单元格，则最终的标签将显示为 `"20-50 (N=100)"`。
> - `@lb`：代表每个区域的下限值。
> - `@ub`：代表每个区域的上限值。
> - `@n`：代表每个区域的数量。
> - `line`表示线图调用regions的线图

#### 气泡图

```
	geoplot ///
    (area regions) ///
    (point capitals i.size [w=pop98], color(Set1, opacity(50)) mlcolor(%0)) ///
    (label capitals city if pop98>250000, color(black)) ///
    , legend compass sbar(length(300) units(km))
```



![气泡图](/img/image-20240324221747484.png)

1. `(area regions)`：绘制地图区域，表示地理区域的边界或范围。
2. `(point capitals i.size [w=pop98], color(Set1, opacity(50)) mlcolor(%0))`：绘制城市的散点图，其中城市的大小由 `i.size` 决定，颜色使用 `Set1` 调色板，不透明度设置为 `50%`，并且城市标签的颜色为 `%0`，即黑色。城市的大小基于 `pop98` 变量，表示城市的人口数量。
3. `(label capitals city if pop98>250000, color(black))`：标记城市的名称，但只针对人口数量超过 `250,000` 的城市进行标记，标签颜色为黑色。
4. `, legend compass sbar(length(300) units(km))`：添加图例、指南针和比例尺。比例尺的长度设置为 `300` 单位，单位为公里。

#### 局部放大图

```sql
geoplot (area regions)                                           /// 
    (area regions         if id==1, fc(Coral*.5) lc(gray))       /// 
    (label regions region if id==1, color(black))                /// 
    (area regions         if id==1, fc(Coral) lc(gray) /*
                                 */ box(circle pad(5) fc(gs14))) /// 
    (pie regions relig1 relig2 relig3 if id==1, lab(, reverse))  /// 
    , legend(pos(se) rowgap(1)) zoom(4/5: 6 90 210)
```

- `(area regions)`：绘制地图区域，表示地理区域的边界或范围。
- `(area regions if id==1, fc(Coral*.5) lc(gray))`：根据条件 `id==1` 绘制特定区域的地图区域，填充颜色为 `Coral*.5`，边界线颜色为灰色。
- `(label regions region if id==1, color(black))`：标记特定区域的名称，但只对 `id==1` 的区域进行标记，标签颜色为黑色。
- `(area regions if id==1, fc(Coral) lc(gray) /* ... */ box(circle pad(5) fc(gs14)))`：根据条件 `id==1` 绘制特定区域的地图区域，并在周围添加一个填充色为 `Coral` 的框，边界线颜色为灰色。
- `(pie regions relig1 relig2 relig3 if id==1, lab(, reverse))`：在特定区域绘制饼图，但只对 `id==1` 的区域进行绘制。饼图中包含 `relig1`、`relig2` 和 `relig3` 变量的数据，标签反向显示。
- `, legend(pos(se) rowgap(1))`：设置图例位置为东南方向，行间距为 `1`。
- `zoom(4/5: 6 90 210)`：设置地图的放大比例为 `4/5`，并指定地图显示的范围。
- ![局部放大和饼图](/img/image-20240324222316758.png)

## 地图使用规范

[自然资源部关于印发《公开地图内容表示规范》的通知](https://www.gov.cn/gongbao/content/2023/content_5752310.htm)

[规范使用地图 一点都不能错](http://politics.people.com.cn/n1/2022/0830/c1001-32514471.html)

省流：使用单个省份地图，街道乡镇地图还行，使用我国整体的地图是比较麻烦的。

- 在使用我国整体地图时，比例画幅要求严格。
- 轮廓线，有些国界暂时未定或者每年有细微变动。
- 领土问题：香港、澳门、台湾、海南诸岛、钓鱼岛等等...
- 九段线最不能缺！
- 不能出现军工等机密数据的标注。
- 图例问题和指北针最好加上且和官方保持一致。

针对期刊，最好参考：[科技期刊地图插图的规范绘制和常见问题](https://www.cjstp.cn/article/2021/1001-7143/1001-7143-32-6-699.shtml)

最官方的地图详见：[标准地图服务](http://bzdt.ch.mnr.gov.cn/index.html)。自己画好地图后也可以在这里拿去送审。

> 官方是不提供shap文件的，只提供eps和jpg文件。
>
> 市面上流行的shap官方文件都是个人制作，需要仔细辨别。
