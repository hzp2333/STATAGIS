clear all
global path "D:\Desktop\efficiency_tree"

cd $path

import excel ".\city_inefficiency_tree.xlsx", firstrow clear

replace group = "1E" if group == "E"
replace group = "2C" if group == "C"
replace group = "3W" if group == "W"
cap replace group = "2C" if group == ""

gen intensity = CO2 / Y      //  1 billion

bys id: egen Ymean = mean(Y)
bys id: egen intensitymean = mean(intensity)
duplicates drop id, force
save ".\temp\fig2Pre.dta",replace



use ".\chinamap\chinacity40_db.dta",clear
rename 市代码 city_code  
merge 1:1 city_code using ".\temp\fig2Pre.dta"
replace Ymean = -100 if missing(Ymean)
replace intensitymean = -100 if missing(intensitymean)

*** GDP
graph set window fontface "Times New Roman"

grmap Ymean using ".\chinamap\chinacity40_coord.dta", ///
 id(ID) line(data(".\chinamap\chinaprov40_line_coord3.dta") by(group) ///
		select(drop if group == 7 | group == 4) ///
		size(vvthin *1 *0.5 *0.5 *0.5) pattern(solid ...) ///
		color(gray%20 /// 
			  black /// 
			  "0 85 170" /// 
			  black /// 
			  black /// 
			  )) ///
	polygon(data(".\chinamap\polygon3") fcolor(black) ///
		osize(vvthin)) ///
	label(data(".\chinamap\chinaprov40_label3") x(X) y(Y) label(ename) length(20) size(*0.8) select(keep if inlist(cname, "N", "1000km", "南海诸岛"))) ///
	clmethod(custom) clbreaks(-100 0 100 200 300  100000) ///
	fcolor(gray "252 255 164" "252 181 25" "237 105 37" "187 55 84" "120 28 109" "51 10 95"  ) ///
legend(order(2 "no data" 3 "0～100" 4 "100～200" 5 "200～300" 6  ">300" ) ///
	ti("", size(*1) pos(11) color(black)) color(black) size(*2)) ///
	osize(vvthin ...) ///
	ocolor(white ...) ///
	graphr(margin(zero)) ///
	subti("GDP (unit: Billion CNY)",size(*1.5)) 
	gr save ".\result\Figure21-chinamapGDP.gph", replace

******************intensitymean
grmap intensitymean using ".\chinamap\chinacity40_coord.dta", ///
 id(ID) line(data(".\chinamap\chinaprov40_line_coord3.dta") by(group) ///
		select(drop if group == 7 | group == 4) ///
		size(vvthin *1 *0.5 *0.5 *0.5) pattern(solid ...) ///
		color(gray%20 /// 
			  black /// 
			  "0 85 170" /// 
			  black /// 
			  black /// 
			  )) ///
	polygon(data(".\chinamap\polygon3") fcolor(black) ///
		osize(vvthin)) ///
	label(data(".\chinamap\chinaprov40_label3") x(X) y(Y) label(ename) length(20) size(*0.8) select(keep if inlist(cname, "N", "1000km", "南海诸岛"))) ///
	clmethod(custom) clbreaks(-100 0 5 10 15 1200 ) ///
	fcolor(gray "252 255 164" "252 181 25" "237 105 37" "187 55 84" "120 28 109" "51 10 95"  ) ///
legend(order(2 "no data" 3 "0～5" 4 "5～10" 5 "10～150" 6  ">150" ) ///
	ti("", size(*1) pos(11) color(black)) color(black) size(*2)) ///
	osize(vvthin ...) ///
	ocolor(white ...) ///
	graphr(margin(zero)) ///
	subti("Carbon intensity (unit: 10{sup:4} tons/Billion CNY)" ,size(*1.5)) 
	gr save ".\result\Figure22-chinamapCI.gph", replace
	
gr combine  ".\result\Figure21-chinamapGDP.gph" ".\result\Figure22-chinamapCI.gph" ,  xsize(4) ysize(2) imargin(zero) graphregion(margin(zero))  plotr(m(zero)) rows(1)

gr export ".\result\Figure 2 Regional gross output and carbon emission intensity across Chinese cities.png", replace  width(4600) 







cd $path
import excel using ".\temp\fig4Pre.xlsx",first clear
save ".\temp\fig4Pre.dta",replace
 
 

use ".\chinamap\chinacity40_db.dta",clear
rename 市代码 city_code  
merge 1:1 city_code using ".\temp\fig4Pre.dta"


rename group typee
codebook typee
encode typee ,gen(type)

replace type = -100 if missing(type)

graph set window fontface "Times New Roman"


grmap type using ".\chinamap\chinacity40_coord.dta", ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(-1111 0 1 2 3 4 5 6 7 8 9 10) ///
	fcolor(gray "226 16 52" "251 68 195"  "247 208 70" "253 255 112" "26 241 28" green "130 247 222" "8 72 239"  ///
  "117 52 118"   "122 30 235"  ) ///
	legend(size(*1.3) ///
	order(2 "no data" 3 "group 1" 4 "group 2" 5 "group 3" 6 "group 4" 7 "group 5" 8 "group 6" 9 "group 7"  10 "group 8"  11 "group 9" 12 "group 10") ti("", size(*0.5) pos(11) color(black)) color(black) ) ///
		graphr(margin(medium)) ///
	line(data(".\chinamap\chinaprov40_line_coord.dta") by(group) select(drop if group == 7 | group == 4) size(vthin *1 *0.5 *1.2 *0.5 *0.5 *1.2) pattern(solid ...) ///
		color(gray%20 /// 
			  black /// 
			  "0 85 170" /// 
			  black /// 
			  black /// 
			  )) ///
	polygon(data(".\chinamap\polygon") fcolor(black) ///
		osize(vvthin)) ///
	label(data(".\chinamap\chinaprov40_label") x(X) y(Y) label(ename) length(20) size(*0.8) select(keep if inlist(cname, "N", "1000km", "南海诸岛"))) ///
	subti("Groups obtained by the efficiency tree method" ,size(*1)) 

	gr export ".\result\Figure 4 Groups obtained from efficiency tree.png", replace width(4600) 

// sort typee
//
// <<<<
// <<<>
// <<>
// <>
// ><<<
// ><<>
// ><><
// ><>>
// >><
// >>>



***********************************************
cd $path

use   ".\chinamap\chinacity40_db.dta"   ,clear
rename 市代码 city_code  
merge 1:1 city_code using ".\temp\fig7Pre.dta"
replace enveff_tree3 = -100 if missing(enveff_tree3)
replace enveff_region3 = -100 if missing(enveff_region3)

*** enveff_tree3
graph set window fontface "Times New Roman"

grmap enveff_tree3 using ".\chinamap\chinacity40_coord.dta", ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(-1000 -100  0.2 0.4 0.6 0.8 1  ) ///
	fcolor(gray "252 255 164" "252 181 25" "237 105 37" "187 55 84" "120 28 109"   ) ///
	legend( order(2 "no data" 3 "0～0.2" 4 "0.2～0.4" 5 "0.4～0.6" 6 "0.6～0.8" 7 "0.8～1" ) ///
	ti("", size(*0.5) pos(11) color(black)) color(black) size(*2)) ///
		graphr(margin(medium)) ///
	line(data(".\chinamap\chinaprov40_line_coord.dta") by(group) select(drop if group == 7 | group == 4) size(vthin *1 *0.5 *1.2 *0.5 *0.5 *1.2) pattern(solid ...) ///
		color(gray /// 
			  black /// 
			  "0 85 170" /// 
			  black /// 
			  black /// 
			  )) 	  ///
	polygon(data(".\chinamap\polygon.dta") fcolor(black) ///
		osize(vvthin)) ///
	label(data(".\chinamap\chinaprov40_label.dta") x(X) y(Y) label(ename) length(20) size(*0.8) select(keep if inlist(cname, "N", "1000km", "南海诸岛"))) ///
		subti("mean value of efficiency obtained by efficiency tree grouping" ,size(*1.5)) 
	gr save ".\result\Figure71-chinamapenveff_tree.gph", replace
	
** enveff_region3
grmap enveff_region3 using ".\chinamap\chinacity40_coord.dta", ///
	id(ID) osize(vvthin ...) ocolor(white ...) ///
	clmethod(custom) clbreaks(-1000 -100  0.2 0.4 0.6 0.8 1  ) ///
	fcolor(gray "252 255 164" "252 181 25" "237 105 37" "187 55 84" "120 28 109"   ) ///
	legend( order(2 "no data" 3 "0～0.2" 4 "0.2～0.4" 5 "0.4～0.6" 6 "0.6～0.8" 7 "0.8～1" ) ///
	ti("", size(*0.5) pos(11) color(black)) color(black) size(*2)) ///
		graphr(margin(medium)) ///
	line(data(".\chinamap\chinaprov40_line_coord.dta") by(group) select(drop if group == 7 | group == 4) size(vthin *1 *0.5 *1.2 *0.5 *0.5 *1.2) pattern(solid ...) ///
		color(gray /// 省界颜色
			  black /// 国界线颜色
			  "0 85 170" /// 海岸线颜色
			  black /// 小地图框格颜色
			  black /// 比例尺和指北针颜色
			  )) 	  ///
	polygon(data(".\chinamap\polygon.dta") fcolor(black) ///
		osize(vvthin)) ///
	label(data(".\chinamap\chinaprov40_label.dta") x(X) y(Y) label(ename) length(20) size(*0.8) select(keep if inlist(cname, "N", "1000km", "南海诸岛"))) ///
	subti("mean value of efficiency obtained by geographical grouping" ,size(*1.5)) 
	
	gr save ".\result\Figure72-chinamapenveff_region.gph", replace
	
gr combine  ".\result\Figure71-chinamapenveff_tree.gph" ".\result\Figure72-chinamapenveff_region.gph" ,  xsize(4) ysize(2) imargin(zero) graphregion(margin(zero))  plotr(m(zero)) rows(1)
	
	gr export ".\result\Figure 7 Comparison on carbon emission efficiency.png", replace  width(4600) 

	

cd $path
import excel using "city_inefficiency_tree.xlsx",first clear

rename CO2 C
keep if year >=2010

global control Y C K L E fdi open tech human

replace Y = Y/10
replace K = K/10

xtset id year

replace group = "East" if group == "E"
replace group = "Central" if group == "C"
replace group = "West" if group == "W"

replace group = "1East" if group == "East"
replace group = "2Central" if group == "Central"
replace group = "3West" if group == "West"


****************Table 2**Descriptive statistics*********************
logout , save("result\table2.xls") excel replace:tabstat $control , by(group) stats(n mean sd min max ) col(s) f(%6.3f) long 


