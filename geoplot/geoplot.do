clear

ssc install geoplot, replace
ssc install palettes, replace
ssc install colrspace, replace
ssc install moremata, replace

cd F:\桌面\GIS_sum\geoplot

local url http://fmwww.bc.edu/repec/bocode/i/
geoframe create regions  `url'Italy-RegionsData.dta, id(id) coord(xcoord ycoord) ///
shpfile(Italy-RegionsCoordinates.dta)
geoframe create country  `url'Italy-OutlineCoordinates.dta
geoframe create capitals `url'Italy-Capitals.dta, coord(xcoord ycoord)
geoframe create lakes    `url'Italy-Lakes.dta, feature(water)
geoframe create rivers   `url'Italy-Rivers.dta, feature(water)


geoplot (area regions) 
(line country, lwidth(medthick))

geoplot (line regions)

geoplot (area regions fortell, label("@lb-@ub (N=@n)")) (line regions)

geoplot (area regions fortell, levels(20) lcolor(gray)) ///
    , clegend(height(30)) zlabel(4(3)28)
	
	
	geoplot ///
    (area regions) ///
    (point capitals i.size [w=pop98], color(Set1, opacity(50)) mlcolor(%0)) ///
    (label capitals city if pop98>250000, color(black)) ///
    , legend compass sbar(length(300) units(km))
	
	
geoplot ///
    (area regions fortell) ///
    (point capitals i.size [w=pop98], color(Set1, reverse opacity(50)) ///
        mlcolor(white)) ///
    , legend(layout(- "FORTELL" 1 | - "CITY SIZE" 2) position(sw))
	
	

geoplot (area regions)                                           /// 1
    (area regions         if id==1, fc(Coral*.5) lc(gray))       /// 2
    (label regions region if id==1, color(black))                /// 3
    (area regions         if id==1, fc(Coral) lc(gray) /*
                                 */ box(circle pad(5) fc(gs14))) /// 4
    (pie regions relig1 relig2 relig3 if id==1, lab(, reverse))  /// 5
    , legend(pos(se) rowgap(1)) zoom(4/5: 6 90 210)