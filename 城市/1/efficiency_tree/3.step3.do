clear all
global path "d:\Desktop\efficiency_tree"
cd "$path"

import excel using ".\temp\to_ddf_by_group.xlsx",first clear


encode group ,gen(groupid)

forvalues ii = 1/10{
	preserve
		keep if groupid == `ii' 
		xtset id year
		gen Row=_n
		

		gen gk=0*K
		gen gl=0*L
		gen ge=0*E
		gen gy=1*Y
		gen gc=-1*CO2
		
		cd "$path\temp"
		teddf K L E= Y:CO2 , dmu(id)  gx(gk gl ge) gy(gy) gb(gc) sav(ddf`ii'.dta,replace)
		
		merge m:m  Row  using "ddf`ii'.dta"
		drop _merge

		bys id: mipolate Dv year, linear gen(Dv2)

		gen enveff = 1- Dv2
		save "ddf`ii'.dta",replace
	restore	
}

use "ddf1.dta",clear
forvalues ii = 2/10{
append using "ddf`ii'.dta"
}
rename enveff enveff_tree

cd "$path"

save ".\temp\ddf_tree.dta",replace



import excel using ".\temp\to_ddf_by_group.xlsx",first clear

gen region = 0
replace region = 1 if inlist(provs,"广东","海南")
replace region = 1 if inlist(provs,"北京","天津","河北","辽宁","山东","江苏","上海","浙江","福建")
  replace region = 2 if inlist(provs,"黑龙江","吉林林","山西","河南","安徽","湖北","湖南","江西")
  replace region = 3 if inlist(provs,"青海","新疆")
  replace region = 3 if inlist(provs,"内蒙古","宁夏","陕西","重庆","四川","贵州","广西","云南","甘肃") 
la def region 1 "east" 2 "central" 3 "west", modify
la val region region
	
forvalues ii = 1/3{
	preserve
		keep if region == `ii' 
		xtset id year
		
		gen Row=_n

		gen gk=0*K
		gen gl=0*L
		gen ge=0*E
		gen gy=1*Y
		gen gc=-1*CO2
		
		cd "$path\temp"
		teddf K L E= Y:CO2 , dmu(id)  gx(gk gl ge) gy(gy) gb(gc) sav(ddfregion`ii'.dta,replace)
		
		merge m:m  Row  using "ddfregion`ii'.dta"
		drop _merge

		bys id: mipolate Dv year, linear gen(Dv2)

		gen enveff = 1- Dv2

		save "ddfregion`ii'.dta",replace

	restore	
}

use "ddfregion1.dta",clear
forvalues ii = 2/3{
append using "ddfregion`ii'.dta"
}
rename enveff enveff_region

cd "$path"

save ".\temp\ddf_region.dta",replace


use ".\temp\ddf_tree.dta",clear
bys year:egen enveff_tree2 = mean(enveff_tree)
keep if id ==1
keep enveff_tree2 year
save ".\temp\ddf_tree2.dta",replace

use ".\temp\ddf_region.dta",clear
bys year:egen enveff_region2 = mean(enveff_region)
keep if id ==1
keep enveff_region2 year
save ".\temp\ddf_region2.dta",replace

merge 1:1 year using ".\temp\ddf_tree2.dta"
save ".\temp\CEEm_CEEregion_by_year.dta",replace

twoway ( line enveff_tree2 year,lwidth(medthick)) ///
(line enveff_region2 year,lwidth(medthick)) , ///
legend(order(1 "enveff_tree" 2 "enveff_region" )) ///
xlabel(2010(1)2018,angle(60)  labsize(small)) 

gr export ".\temp\fig2两种方法比较.png", replace width(2600) 


cd "$path"

use ".\temp\ddf_tree.dta",clear
bys id:egen enveff_tree3 = mean(enveff_tree)
keep if year == 2010

keep enveff_tree3 city_code
save ".\temp\ddf_tree3.dta",replace

use ".\temp\ddf_region.dta",clear
bys id:egen enveff_region3 = mean(enveff_region)
keep if year == 2010
keep enveff_region3 city_code
save ".\temp\ddf_region3.dta",replace
merge 1:1 city_code using ".\temp\ddf_tree3.dta"
save ".\temp\CEEm_CEEregion_by_id.dta",replace


drop _merge
save ".\temp\fig7Pre.dta",replace

	cd "$path"
import excel using ".\temp\to_ddf_by_group.xlsx",first clear

xtset id year
gen Row=_n

gen gk=0*K
gen gl=0*L
gen ge=0*E
gen gy=1*Y
gen gc=-1*CO2
		
cd "$path\temp"
teddf K L E= Y:CO2 , dmu(id)  gx(gk gl ge) gy(gy) gb(gc) sav(ddf_global.dta,replace)

merge m:m  Row  using "ddf_global.dta"
drop _merge

bys id: mipolate Dv year, linear gen(Dv2)

gen enveff = 1- Dv2
rename enveff enveff_global
cd "$path"
save ".\temp\ddf_global.dta",replace


use ".\temp\ddf_tree.dta",clear
merge 1:1 city_code year using ".\temp\ddf_region.dta"
drop _merge
merge 1:1 city_code year using ".\temp\ddf_global.dta"
drop _merge
save ".\temp\CEEm_CEEregion_CEE_global_by_id_year.dta",replace


// ------------ //
use ".\temp\CEEm_CEEregion_CEE_global_by_id_year.dta",clear
rename (enveff_tree enveff_region enveff_global) (CEEm CEEr CEEG)
gen TGIm = CEEm - CEEG 
gen TGIr = CEEr - CEEG
gen CEIm = 1 - CEEm
// 1e-20
replace CEIm = 0 if  CEIm<= 1e-10  
replace TGIm = 0 if  TGIm<= 1e-10  

gen CERm = CEIm * CO2
gen CERTGm = TGIm * CO2

keep id year groupid CERm CERTGm  CO2 Y E CEIm TGIm  

label variable id "城市" 
label variable year "年份" 
label variable groupid "效率树分组" 
label variable CERm "按效率树分组得到的组内碳排放非效率*碳排放总量=碳减排1" 
label variable CERTGm "（全局碳排放非效率 - 按效率树分组得到的组内碳排放非效率）*碳排放总量=碳减排2" 
label variable CO2 "碳排放总量" 
label variable Y "产出" 
label variable E "能源使用量" 
label variable CEIm "按效率树分组得到的组内碳排放非效率" 
xtset id year



forvalues ii = 1/10{
	preserve
	 keep if groupid == `ii'
gen C_it_d_E_it =  CO2/E  
gen C_it_d_Y_it =  CO2/Y  

gen E_it_d_Y_it =  E/Y
bys  year: egen Y_t = sum(Y)
gen Y_it_d_Y_t =  Y/Y_t
bys  year: egen CERTGm2 = sum(CERTGm)
bys  year: egen CERm2 = sum(CERm)
xtset  year id

cd "$path\temp"


keep if year == 2010 | year ==2018
. lmdi CERm2 = CEIm C_it_d_Y_it  Y , t(year) over(id ) add saving(lmdi_zunei`ii') replace	
	use "lmdi_zunei`ii'.dta",clear
	drop if Dtot==.
	gen groupid =`ii'
	save "lmdi_zunei`ii'.dta",replace
	restore
} 

use "lmdi_zunei1.dta",clear

forvalues ii = 2/10{
append using "lmdi_zunei`ii'.dta"

}
cd "$path\temp"
save "lmdi_management_failure.dta",replace


********************************************

// ssc install lmdi 
cd "$path"

use ".\temp\CEEm_CEEregion_CEE_global_by_id_year.dta",clear
rename (enveff_tree enveff_region enveff_global) (CEEm CEEr CEEG)
gen TGIm = CEEm - CEEG 
gen TGIr = CEEr - CEEG
gen CEIm = 1 - CEEm
// 1e-20
replace CEIm = 0 if  CEIm<= 1e-10  
replace TGIm = 0 if  TGIm<= 1e-10  

gen CERm = CEIm * CO2
gen CERTGm = TGIm * CO2

keep id year groupid CERm CERTGm  CO2 Y E CEIm TGIm  

label variable id "城市" 
label variable year "年份" 
label variable groupid "效率树分组" 
label variable CERm "按效率树分组得到的组内碳排放非效率*碳排放总量=碳减排1" 
label variable CERTGm "（全局碳排放非效率 - 按效率树分组得到的组内碳排放非效率）*碳排放总量=碳减排2" 
label variable CO2 "碳排放总量" 
label variable Y "产出" 
label variable E "能源使用量" 
label variable CEIm "按效率树分组得到的组内碳排放非效率" 
xtset id year




forvalues ii = 1/10{
	preserve
	 keep if groupid == `ii'
gen C_it_d_E_it =  CO2/E  
gen C_it_d_Y_it =  CO2/Y  
gen E_it_d_Y_it =  E/Y
bys  year: egen Y_t = sum(Y)
gen Y_it_d_Y_t =  Y/Y_t
bys  year: egen CERTGm2 = sum(CERTGm)
bys  year: egen CERm2 = sum(CERm)
xtset  year id

cd "$path\temp"


keep if year == 2010 | year ==2018
. lmdi CERTGm2 = TGIm C_it_d_Y_it  Y  , t(year) over(id ) add saving(lmdi_gap`ii') replace
	use "lmdi_gap`ii'.dta",clear
	drop if Dtot==.
	gen groupid =`ii'
	save "lmdi_gap`ii'.dta",replace
	restore
} 

use "lmdi_gap1.dta",clear

forvalues ii = 2/10{
append using "lmdi_gap`ii'.dta"

}
cd "$path\temp"
save "lmdi_technological_gap.dta",replace


