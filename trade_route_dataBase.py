from Colony_dataBase import *


def trade_route(start,end,profit):
    return [start,end,profit]
def trade_start_colony(route):
    return route[0]
def trade_end_colony(route):
    return route[1]
def trade_profit(route):
    return route[2]
def switch_route(route):
    return trade_route(trade_end_colony(route),trade_start_colony(route),trade_profit(route))

route1 = trade_route(Acapulco_De_Juarez,London,500)
route2 = trade_route(Acapulco_De_Juarez,Papeete,325)
route3 = trade_route(Amsterdam,Lima,550)
route4 = trade_route(Amsterdam,Rio_De_Janeiro,350)
route5 = trade_route(Amsterdam,Shanghai,600)
route6 = trade_route(Anchorage,Honolulu,275)
route7 = trade_route(Calcutta,Reykjavik,600)
route8 = trade_route(Cape_Verde,Lima,450)
route9 = trade_route(Freetown,Dares_Salaam,400)
route10 = trade_route(Jacksonville,London,350)
route11 = trade_route(Jacksonville,Mumbai,575)
route12 = trade_route(Jacksonville,Valparaiso,400)
route13 = trade_route(London,Havana,350)
route14 = trade_route(London,New_York,320)
route15 = trade_route(London,Wellington,600)
route16 = trade_route(Manila,Acapulco_De_Juarez,400)
route17 = trade_route(Maracaibo,Freetown,330)
route18 = trade_route(Mumbai,Perth,300)
route19 = trade_route(Mumbai,Suva,350)
route20 = trade_route(Murmansk,Benguela,400)
route21 = trade_route(Murmansk,Istanbul,350)
route22 = trade_route(Murmansk,Veracruz,400)
route23 = trade_route(New_York,Calcutta,600)
route24 = trade_route(Newfoundland,Amsterdam,325)
route25 = trade_route(Nuuk,Murmansk,325)
route26 = trade_route(Port_Moresby,Honolulu,325)
route27 = trade_route(Recife,Antofagasta,360)
route28 = trade_route(Rio_De_Janeiro,Amsterdam,360)
route29 = trade_route(San_Francisco,Honolulu,275)
route30 = trade_route(San_Francisco,New_York,500)
route31 = trade_route(San_Francisco,Sydney,500)
route32 = trade_route(San_Francisco,Hong_Kong,400)
route33 = trade_route(Shanghai,New_York, 600)
route34 = trade_route(Sydney,Papeete,320)
route35 = trade_route(Tokyo,Lima,450)
route36 = trade_route(Tokyo,Sydney,325)
route37 = trade_route(Tokyo,Wellington,325)
route38 = trade_route(Tokyo,Yangon,350)
route39 = trade_route(Vancouver,Lima,375)
route40 = trade_route(Vladivostok,Anchorage,330)
route41 = trade_route(Vladivostok,Honolulu,325)
route42 = trade_route(Vladivostok,Mumbai,400)
route43 = trade_route(Walvis_Bay,Buenos_Aires,325)
route44 = trade_route(Wellington,Papeete,275)

route45 = switch_route(route1)
route46 = switch_route(route2)
route47 = switch_route(route3)
route48 = switch_route(route4)
route49 = switch_route(route5)
route50 = switch_route(route6)
route51 = switch_route(route7)
route52 = switch_route(route8)
route53 = switch_route(route9)
route54 = switch_route(route10)
route55 = switch_route(route11)
route56 = switch_route(route12)
route57 = switch_route(route13)
route58 = switch_route(route14)
route59 = switch_route(route15)
route60 = switch_route(route16)
route61 = switch_route(route17)
route62 = switch_route(route18)
route63 = switch_route(route19)
route64 = switch_route(route20)
route65 = switch_route(route21)
route66 = switch_route(route22)
route67 = switch_route(route23)
route68 = switch_route(route24)
route69 = switch_route(route25)
route70 = switch_route(route26)
route71 = switch_route(route27)
route72 = switch_route(route28)
route73 = switch_route(route29)
route74 = switch_route(route30)
route75 = switch_route(route31)
route76 = switch_route(route32)
route77 = switch_route(route33)
route78 = switch_route(route34)
route79 = switch_route(route35)
route80 = switch_route(route36)
route81 = switch_route(route37)
route82 = switch_route(route38)
route83 = switch_route(route39)
route84 = switch_route(route40)
route85 = switch_route(route41)
route86 = switch_route(route42)
route87 = switch_route(route43)
route88 = switch_route(route44)

routes = [ route1, route2, route3, route4, route5, 
route6, route7, route8, route9, route10, route11, 
route12, route13,route14, route15, route16, route17, 
route18, route19, route20, route21, route22, route23, 
route24, route25, route26, route27, route28, route29, 
route30, route31, route32, route33, route34, route35, 
route36, route37, route38,route39, route40, route41, 
route42, route43, route44, route45, route46, route47, 
route48, route49, route50, route51, route52, route53, 
route54, route55, route56, route57, route58, route59, 
route60, route61, route62, route63, route64, route65, 
route66, route67, route68, route69, route70, route71, 
route72, route73, route74, route75, route76, route77, 
route78, route79, route80, route81, route82, route83, 
route84, route85, route86, route87, route88 ]