CREATE TABLE colony AS
    SELECT 01 AS number,"Vancouver" AS name, "D10" AS coordinate, 20 AS tax, 15 AS parking_fee, "North America" AS continent, "wood" AS resource  UNION
    SELECT 02,"San Francisco", "D9",  20, 20, "North America", "metal" UNION
    SELECT 03, "Honolulu", "B8", 20, 20, "Oceania", "fertilizer" UNION
    SELECT 04, "Acapulco de Juarez",  "F8 LOWER", 20, 15,  "North America", "arm" UNION
    SELECT 05, "Panama Canal", "G7", 40,  30,  "North America", "canal"  UNION
    SELECT 06,  "Galapagos Islands", "F6",  20, 15, "South America", "fertilizer" UNION
    SELECT 07, "Lima", "G6",                 20,        20,                "South America",               "gold"              UNION
    SELECT 08,            "Papeete",        "B5",                 20,        10,                      "Oceania",               "arm"               UNION
    SELECT 09,        "Antofagasta",        "H5",                 20,        15,                "South America",               "arm"               UNION
    SELECT 10,         "Valparaiso",        "H4",                 20,        15,                "South America",               "metal"             UNION
    SELECT 11,   "Tierra del Fuego",        "H3",                 30,        15,                "South America",               "arm"               UNION
    SELECT 12,       "Buenos Aires",        "I4",                 20,        15,                "South America",               "arm"               UNION
    SELECT 13,     "Rio de Janeiro",        "J7",                 20,        20,                "South America",               "wood"              UNION
    SELECT 14,             "Recife",        "J6",                 20,        10,                "South America",               "wood"              UNION
    SELECT 15,   "Strait Of Bering",       "A11",                 30,        15,                       "Strait",               "Strait"            UNION
    SELECT 16,          "Maracaibo",        "H7",                 20,        20,                "South America",               "oil"               UNION
    SELECT 17,      "Santo Domingo",        "H8",                 20,        15,                "North America",               "sugar"             UNION
    SELECT 18,             "Havana",        "G8",                 20,        15,                "North America",               "sugar"             UNION
    SELECT 19,           "Veracruz",  "F8 UPPER",                 20,        15,                "North America",               "gold"              UNION
    SELECT 20,       "Jacksonville",        "G9",                 20,        20,                "North America",               "wood"              UNION
    SELECT 21,           "New York",        "H9",                 20,        15,                "North America",               "capital"           UNION
    SELECT 22,       "Newfoundland",       "I10",                 30,        15,                "North America",               "oil"               UNION
    SELECT 23,               "Nuuk",       "I11",                 20,        15,                "North America",               "oil"               UNION
    SELECT 24,          "Reykjavik",       "K11",                 20,        10,                       "Europe",               "arm"               UNION
    SELECT 25,           "Murmansk",       "O11",                 20,        10,                       "Europe",               "capital"           UNION
    SELECT 26,      "St Petersburg",       "N10",                 20,        10,                       "Europe",               "metal"             UNION
    SELECT 27,          "Amsterdam",       "M10",                 20,        20,                       "Europe",               "wood"              UNION
    SELECT 28,             "London",       "L10",                  20,       20,                       "Europe",               "capital"           UNION
    SELECT 29, "Strait Of Gibratar",        "L9",                  30,       15,                       "Strait",               "Strait"            UNION
    SELECT 30,              "Tunis",        "M9",                  20,      15,                        "Africa",                "oil"              UNION
    SELECT 31,           "Istanbul",        "N9",                  20,      15,                        "Europe",               "metal"             UNION
    SELECT 32,          "Cape Verde",       "K8",                  20,      20,                        "Africa",               "arm"               UNION
    SELECT 33,          "Freetown",         "L7",                 20,       15,                         "Africa", "gold" UNION
    SELECT 34,              "Lagos",        "M7",                 20,      15, "Africa", "wood" UNION
    SELECT 35,          "Benguela",          "M6",                 20,      15, "Africa", "wood" UNION
    SELECT 36,  "Cape of Good Hope",        "N4",                  30,     15, "Africa", "arm" UNION
    SELECT 37,  "Strait of Mozambique",      "O5",                 30,     15, "Strait", "Strait" UNION
    SELECT 38,          "Port Louis",       "P5",                 20,     10, "Africa", "sugar" UNION
    SELECT 39,          "Dares Salaam",      "O6",                20,      15, "Africa", "metal" UNION
    SELECT 40,          "Mogadishu",        "P7",                  20,     10, "Africa", "arm" UNION
    SELECT 41,      "Strait of Mandeb",    "O7 UPPER",            30,     15, "Strait", "Strait" UNION
    SELECT 42,          "Suez Canal",       "O9",                40,     30,"Africa", "canal" UNION
    SELECT 43,      "Strait Of Hormuz",     "P8",                30,      15, "Strait", "Strait" UNION
    SELECT 44,               "Mumbai",      "Q8",               20,   15, "Asia", "oil" UNION
    SELECT 45,              "Colombo",      "R7",               20,   20, "Asia", "wood" UNION
    SELECT 46,              "Calcutta",     "R8",               20,   15, "Asia", "oil" UNION
    SELECT 47,              "Yangon",       "S8",               20,   10, "Asia", "metal" UNION
    SELECT 48,      "Strait of Malacca",    "S7",                30,   15, "Strait", "Strait" UNION
    SELECT 49,              "Hong Kong",    "T8",               20,   20, "Asia", "sugar" UNION
    SELECT 50,              "Jakarta",      "T6",   20,   20, "Asia", "wood" UNION
    SELECT 51,              "Perth",        "T4",   20,   20, "Oceania", "arm" UNION
    SELECT 52,              "Shanghai",     "U9",   20, 20, "Asia", "capital" UNION
    SELECT 53,               "Tokyo",       "V9",     20,     20, "Asia", "capital" UNION
    SELECT 54,          "Vladivostok",      "V10", 20,    15, "Asia", "wood" UNION
    SELECT 55,           "Sydney",          "W4",   20,     15, "Oceania","gold" UNION
    SELECT 56,           "Wellington",      "X4", 20,     15, "Oceania", "wood" UNION
    SELECT 57,            "Port Moresby",   "V6",   20, 10, "Oceania", "wood" UNION
    SELECT 58,               "Darwin",      "U6",   20,     10, "Oceania", "capital" UNION
    SELECT 59,              "Male",         "Q7",   20,     20, "Asia", "arm" UNION
    SELECT 60,                  "Yaren",    "X7",  20,     10, "Oceania", "fertilizer" UNION
    SELECT 61,          "Walvis Bay",       "M5",  20,     15, "Africa", "arm" UNION
    SELECT 62,              "Churchill",    "G10", 20,  10, "North America", "oil" UNION
    SELECT 63,                  "Manila",   "U7",   20,     15,     "Asia",     "sugar" UNION
    SELECT 64,                  "Suva",     "X5",   20,     15,     "Oceania",  "sugar" UNION
    SELECT 65,  "Anchorage",     "C10",  20, 10,     "North America","arm";


create table ordered_colony as
    select * from colony order by name;

create table port as
    select * from ordered_colony where tax = 20;

create table choking_point as
    select * from ordered_colony where tax = 30;

create table 20_for_parking as
    select * from ordered_colony where parking_fee = 20;

create table 10_for_parking as
    select * from ordered_colony where parking_fee = 10;

create table 15_for_parking as
    select * from ordered_colony where parking_fee = 15;

create table Asia_colony as
    select * from ordered_colony where continent = "Asia";

create table Europe_colony as
    select * from ordered_colony where continent = "Europe";

create table Africa_colony as
    select * from ordered_colony where continent = "Africa";

create table Oceania_colony as
    select * from ordered_colony where continent = "Oceania";

create table NA_colony as
    select * from ordered_colony where continent = "North America";

create table SA_colony as
    select * from ordered_colony where continent = "South America";

create table canal as
    select * from ordered_colony where resource = "canal";

create table canal as
    select * from ordered_colony where resource = "canal";

create table straits as 
    select * from ordered_colony where continent = "strait";

create table wood_colony as
    select * from ordered_colony where resource = "wood";

create table metal_colony as
    select * from ordered_colony where resource = "metal";

create table fertilizer_colony as
    select * from ordered_colony where resource = "fertilizer";

create table gold_colony as
    select * from ordered_colony where resource = "gold";

create table sugar_colony as
    select * from ordered_colony where resource = "sugar";

create table oil_colony as
    select * from ordered_colony where resource = "oil";

create table arm_colony as
    select * from ordered_colony where resource = "arm";

CREATE TABLE empires as
    SELECT "The United Kingdom" AS name, "London" AS capital, "Yellow " AS color, "Each time collecting tax, 
    you can earn $10 more for eah territory" AS skill UNION
    SELECT "Russia","Murmansk","Red", "You can build a ship with $20 and 
    either a wood ticket or a metal ticket" UNION
    SELECT "China","Shanghai","Green","You can earn $200 more each time 
    for a trade task" UNION
    SELECT "Japan", "Tokyo","Silver/Orange", "You can park at a foreign 
    port or go through a choking point without permission, and the territory 
    owners (not including the pirate) will protect you when at their places." UNION
    SELECT "pirate","Darwin" ,"Black/Purple", "You are always a “chartered 
    pirateer” and a “legal smuggler”. You can rob legally and needn`t pay fees
     when entering foreign territories." UNION
    SELECT  "The United States","New York" ,"Blue" ,"you can build factories 
    on any territory you like, except for gold territories.";

CREATE TABLE trade_route As
    SELECT "Jacksonville" AS point1, "Mumbai" AS point2, 575 AS profit UNION
    SELECT  "Manila",       "Acapulco de Juarez",       400  UNION
    SELECT  "Mumbai",        "Suva" ,                    350    UNION
    SELECT  "Sydney",       "Papeete",                  320   UNION
    SELECT "Maracaibo",     "Freetown",                 330   UNION
    SELECT     "London",       "Havana",                350  UNION
    SELECT  "Tokyo",            "Lima" ,                450  UNION
    SELECT "Rio de Janeiro","Amsterdam", 360  UNION
    SELECT "Recife", "Antofagasta", 360   UNION
    SELECT "Vancouver", "Lima", 375  UNION
    SELECT "Vladivostok", "Anchrage", 330  UNION
    SELECT "Vladivostok", "Honolulu",325   UNION
    SELECT "San Francisco", "Honolulu", 275  UNION
    SELECT "London", "Wellington", 600  UNION
    SELECT "San Francisco", "New York",500  UNION
    SELECT "Jacksonville" , "Valparaiso",400  UNION
    SELECT "Murmansk", "Veracruz", 400  UNION
    SELECT "Vladivostok", "Honolulu",325   UNION
    SELECT "New York", "Calcutta", 600  UNION
    SELECT "Mumbai", "Perth", 300  UNION
    SELECT "Wellington", "Papeete", 275  UNION
    SELECT "Tokyo", "Wellington", 325  UNION
    SELECT "Shanghai", "New York", 600  UNION
    SELECT "Amsterdam", "Rio de Janeiro", 350  UNION
    SELECT "Amsterdam", "Shanghai", 600  UNION
    SELECT "London", "New York", 320   UNION
    SELECT "Tokyo", "Sydney", 325  UNION
    SELECT "Murmansk", "Istanbul", 350  UNION
    SELECT "Acapulco de Juarez", "Papeete", 325  UNION
    SELECT "Nuuk", "Murmansk", 325   UNION
    SELECT "Newfoundland", "Amsterdam", 325  UNION
    SELECT "Jacksonville", "London",350  UNION
    SELECT "Tokyo","Yangon" ,350  UNION
    SELECT "San Francisco", "Sydney", 500   UNION
    SELECT "Freetown", "Dares Salaam", 400  UNION
    SELECT "Amsterdam", "Lima",550  UNION
    SELECT "Murmansk", "Benguela", 400    UNION
    SELECT "San francisco", "Hong Kong", 400   UNION
    SELECT "Port Moresby", "Honolulu",325   UNION
    SELECT "Acapulco de Juarez", "London", 500  UNION
    SELECT "Cape Verde", "Lima", 450  UNION
    SELECT "Vlaivostok", "Mumbai",400  UNION
    SELECT "Calcutta","Rakjavik" ,600   UNION
    SELECT "Anchorage", "Honolulu", 275          UNION
    SELECT "Walvies Bay", "Buenos Aires", 325;

create table short_trade_route as 
    select * from trade_route where profit < 350 order by profit asc;

create table medium_trade_route as
    select * from trade_route where profit < 500 and profit >= 350 order by profit desc;

create table long_trade_route as
    select * from trade_route where profit >= 500 order by profit desc;

create table p1 as 
    select point1, count(*) from trade_table group by point1;

create table p2 as 
    select point2, count(*) from trade_table group by point2;

CREATE TABLE stuff AS 
    SELECT "license" AS type, "junior license" AS name, 50 AS initial_price, 50 AS lowest_price, "used to park at any port without permission for free" AS function UNION
    SELECT "license","senior license",100 ,100 , "used to rob a ship legally" UNION
    SELECT "resource","wood", 15, 10, "used to build ships or factories" UNION
    SELECT "resource","metal",25 ,10 , "used to build ships or factories" UNION
    SELECT "resource","sugar", 30, 15, "used to increase the speed of the ship"UNION
    SELECT "resource","fertilizer",40 , 15, "used to increase the harvest amount of sugar or wood" UNION
    SELECT "resource","oil", 50, 30,"used to increase the possibility to win a war" UNION
    SELECT "resource","gold", 70, 60,"used to protect fortune or pay the equivalent price" ;

create table resource as 
    select * from stuff where type = "resource" order by initial_price;

create table license as 
    select * from stuff where type = "license";