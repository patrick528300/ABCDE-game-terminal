from Colony_dataBase import*

class Resource:
    price = 0
    def __init__(self,name,inital_price=0,lowest_price=0):
        self.name = name
        self.inital_price = inital_price
        self.lowest_price = lowest_price
    

wood = Resource("wood",15,5)  
metal = Resource("metal",25,10)
gold = Resource("gold",70,60)
sugar = Resource("sugar",30,15)
fertilizer = Resource("fertilizer",40,15)
oil = Resource("oil",50,30)
resources = [wood,metal,gold,sugar,fertilizer,oil]


def pandemic (lst): #takes in a list of places
    for i  in lst:
        i.has_pandemic = True
    print("There is a pandemic in the west Africa, ships cannot leave")

def bonus (lst):    # takes in a list of countries
    for i in lst:
        i.money += 200
    print("Every empire gets $200 to promote trades")

def double(lst):     # takes in a list of countries
    for i in lst:
        i.double = True
    print("All the tax are doubled for this rest time")

def half (lst): # takes in a lost of countries
    for i in lst:
        i.half = True
    print("All the tax are reduced by half for this rest time")

def sink():
    print('All ships in Mexico Gulf and Carribean sea sink except for those in ports')

def increased(lst):
    for i in lst:       # takes in a list of resource
        i.price += 10
    print("There is a war in Europe. All resources price is increased by $10")

def decreased(lst):     # takes in a list of resource
    for i in lst:
        i.price -=5
        print("All resources price is increased by $5")

def moveMore():
    print("All the ships can move 1 more block until the next rest time")

def oneMore(lst):       # takes in a list of countries
    piece = 0
    total = 0
    for i in lst:
        for j in i.resource.key():
            i.resource[j] += 1
        lst2  = i.resource.key()
        lst2.remove(gold)
        for k in lst2:
            total += i.resource[k]
        if total > 10:
            for h in i.resource.keys():
                while i.resource[h] > 0 and total > 10:
                    i.resource[h] -= 1
                    total -= 1
    print("All countries can have one more resource")


