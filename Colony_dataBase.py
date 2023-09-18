
class Colony:
    capacity = 3           # can contain three ships maximum
    ships = []              # store what ships are in port 
    factory_built = False   # if this is false then is_green and is_red will be false
    is_green = False        # True if the colony has a green factory
    is_red = False          # True if colony has a red factory
    factory_americanized = False # True if this is built by United States
    no_charge = False       # True if the onwer dont want to set charge for this colony
    has_pandemic = False # True if this colony has a pandemic and ships are not allowed to leave
    def __init__(self,name,coordinate,tax,fee,owner=None,resource=None):
        self.name = name
        self.owner = owner
        self.coordinate = coordinate
        self.tax = tax
        self.fee = fee
        self.resource = resource
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.__repr__()
    

Acapulco_De_Juarez = Colony('Acapulco_De_Juarez','F8 LOWER',20,15,'United States','arm')
Amsterdam = Colony('Amsterdam','M10',20,20,'Pirates','wood')
Anchorage = Colony('Anchorage','C10',20,10,'Japan','arm')
Antofagasta = Colony('Antofagasta','H5',20,15,'China','arm')
Benguela = Colony('Benguela','M6',20,15,'Russia','wood')
Buenos_Aires = Colony('Buenos_Aires','I4',20,15,'United Kingdom','arm')
Calcutta = Colony('Calcutta','R8',20,15,'United States','oil')
Cape_Verde = Colony('Cape_Verde','K8',20,20,'Pirates','arm')
Cape_Of_Good_Hope = Colony('Cape_Of_Good_Hope','N4',30,15,'Japan','arm')
Churchill = Colony('Churchill','G10',20,10,'China','oil')
Colombo = Colony('Colombo','R7',20,20,'Russia','wood')
Darwin = Colony('Darwin','U6',20,10,'Pirates','capital')
Freetown = Colony('Freetown','L7',20,15,'United Kingdom','gold')
Galapagos_Islands = Colony('Galapagos_Islands','F6',20,15,'United States','fertilizer')
Havana = Colony('Havana','G8',20,15,'Pirates','sugar')
Hong_Kong = Colony('Hong_Kong','T8',20,20,'Japan','sugar')
Honolulu = Colony('Honolulu','B8',20,20,'China','fertilizer')
Istanbul = Colony('Istanbul','N9',20,15,'China','metal')
Jacksonville = Colony('Jacksonville','G9',20,20,'Russia','wood')
Lagos = Colony('Lagos','M7',20,15,'United Kingdom','wood')
Lima = Colony('Lima','G6',20,20,'United States','gold')
London = Colony('London','L10',20,20,'United Kingdom','capital')
Male = Colony('Male','Q7',20,20,'Pirates','arm')
Manila = Colony('Manila','U7',20,15,'Japan','sugar')
Maracaibo = Colony('Maracaibo','H7',20,20,'China','oil')
Mogadishu = Colony('Mogadishu','P7',20,20,'Pirates','arm')
Mumbai = Colony('Mumbai','Q8',20,15,'Russia','oil')
Murmansk = Colony('Murmansk','O11',20,10,'Russia','capital')
New_York = Colony('New_York','H9',20,15,'United States','capital')
Newfoundland = Colony('Newfoundland','I10',30,15,'United Kingdom','oil')
Nuuk = Colony('Nuuk','I11',20,15,'United States','oil')
Panama_Canal = Colony('Pamana_Canal','G7',40,30,None,'canal')
Papeete = Colony('Papeete','B5',20,10,'Pirates','arm')
Perth = Colony('Perth','T4',20,20,'Japan','arm')
Port_Louis = Colony('Port_Louis','P5',20,10,'China','suagr')
Port_Moresby = Colony('Port_Moresby','V6',20,10,'Russia','wood')
Recife = Colony('Recife','J6',20,10,'United Kingdom','wood')
Reykjavik = Colony('Reykjavik','K11',20,10,'United States','wood')
Rio_De_Janeiro = Colony('Rio_De_Janeiro','J7',20,20,'Pirates','wood')
San_Francisco = Colony('San_Francisco','D9',20,20,'Japan','metal')
Santo_Domingo = Colony('Santo_Domingo','H8',20,15,'Russia','sugar')
Saint_Petersburg = Colony('Saint_Petersburg','N10',20,10,'United Kingdom','metal')
Bering = Colony('Strait_of_Bering','A11',30,15,'United States')
Gibratar = Colony('Strait_of_Gibratar','L9',30,15,'United Kingdom')
Hormuz = Colony('Strait_of_Hormuz','P8',30,15,'Japan')
Malacca = Colony('Strait_of_Malacca','S7',30,15,'China')
Mandeb = Colony('Strait_of_Mandeb','O7 UPPER',30,15,'Russia')
Mozambique = Colony('Strait_of_Mozambique','O5',30,15,'Pirates')
Suez_Canal = Colony('Suez_Canal','O9',40,30,None,'canal')
Suva = Colony('Suva','X5',20,15,'Pirates','fertilizer')
Tierra_Del_Fuego = Colony('Tierra_Del_Fuego','H3',30,15,'United States','arm')
Tokyo = Colony('Tokyo','V9',20,20,'Japan','capital')
Shanghai = Colony('Shanghai','U9',20,20,'China','capital')
Sydney = Colony('Sydney','W4',20,15,'China','gold')
Tunis = Colony('Tunis','M9',20,15,'Russia','oil')
Valparaiso = Colony('Valparaiso','H4',20,15,'United Kingdom','metal')
Vancouver = Colony('Vancouver','D10',20,15,'United States','wood')
Veracruz = Colony('Veracruz','F8 UPPER',20,15,'Pirates','gold')
Vladivostok = Colony('Vladivostok','V10',20,15,'Japan','wood')
Walvis_Bay = Colony('Walvis_Bay','M5',20,15,'Japan','arm')
Wellington = Colony('Wellington','X4',20,15,'Russia','wood')
Yangon = Colony('Yangon','S8',20,10,'United Kingdom','metal')
Yaren = Colony('Yaren','X7',20,10,'United States','fertilizer')
Jakarta = Colony('Jakarta','T6',20,20,'China','wood')
Dares_Salaam = Colony('Dares_Salaam','O6',20,15,'Japan','metal')



colonies = [ Acapulco_De_Juarez,Amsterdam,Anchorage,Antofagasta,
            Benguela,Buenos_Aires,Calcutta,Cape_Verde,
            Cape_Of_Good_Hope,Churchill,Colombo,Darwin,Freetown,
            Galapagos_Islands,Havana,Hong_Kong,Honolulu,Istanbul,
            Jacksonville,Lagos,Lima,London,Male,Manila,Maracaibo,
            Mogadishu,Mumbai,Murmansk,New_York,Newfoundland,
            Nuuk,Panama_Canal,Papeete,Perth,Port_Louis,Port_Moresby,
            Recife,Reykjavik,Rio_De_Janeiro,San_Francisco,
            Santo_Domingo,Saint_Petersburg,Bering,Gibratar,Hormuz,
            Malacca,Mandeb,Mozambique,Suez_Canal,Suva,Tierra_Del_Fuego,
            Tokyo,Shanghai,Sydney,Tunis,Valparaiso,Vancouver,Veracruz,
            Vladivostok,Walvis_Bay,Wellington,Yangon,
            Yaren,Jakarta,Dares_Salaam ]


#only for initialization - it is not constant - do not use it directly
british_colonies = [i for i in colonies if i.owner == 'United Kingdom']
russian_colonies = [i for i in colonies if i.owner == 'Russia']
chinese_colonies = [i for i in colonies if i.owner == 'China']
japanese_colonies = [i for i in colonies if i.owner == 'Japan']
pirates_colonies = [i for i in colonies if i.owner == 'Pirates'] 
american_colonies = [i for i in colonies if i.owner == 'United States']

#for test 
wood_colonies = [i for i in colonies if i.resource == 'wood']
metal_colonies = [i for i in colonies if i.resource == 'metal']
arm_colonies = [i for i in colonies if i.resource == 'arm']
sugar_colonies = [ i for i in colonies if i.resource == 'sugar']
fertilizer_colonies = [ i for i in colonies if i.resource == 'fertilizer']

west_africa = [Cape_Verde,Lagos,Freetown,Walvis_Bay,Benguela]
north_pacific = [Manila,Hong_Kong,Vladivostok,
                 Shanghai,Anchorage,Vancouver,San_Francisco,Acapulco_De_Juarez]
