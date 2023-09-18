print("***Welcome to ABCDE terminal***")

from Colony_dataBase import *
from trade_route_dataBase import *
from News_function import *

#from random import rand


ship_power = 2
castle_power = 3
senior = 2      # original senior permit amount
junior = 3      # original junior permit amount



class Empire:
    money = 450
    permit = []
    on_trade = False
    ships = []
    route = None
    double = False
    half = False
    resource = {wood:5,metal:5,gold:0,sugar:0,fertilizer:0,oil:0}
    is_robber = False
    def __init__(self,name=None,capital=None,colony=None):
        self.name = name
        self.capital = capital
        self.colony = colony
   
    ###################################################
    # when using data from trade routes,              # 
    # like its starting points and ending points,     #
    # do not break abstraction barrier! use selectors!#
    ###################################################
    def collect_tax(self):
        """
        Loop throught the colony list of the empire`s, 
        add the tax up and get the total tax
        """
        tax = 5 # $5 bonus for having a capital
        # BEGIN PROBLEM 1
        """YOUR CODE HERE"""
        # END PROBLEM 1
        if self.double:
            tax *= 2
            self.double = False
        elif self.half:
            tax //= 2
            self.half = False
        return tax
    

   
   
   
   
   
    def build_factory(self,place,color):
        """
        The function takes in self, a colony object and the factory color.
        It should check if the colony is in the list.
        Then see if the colony already has a green or red factory
        If there is no, spend some amount of resources and money to build one
        Green factory can be upgraded to a Red factory but we cannot do the opposite
        """

        has_red = False
        has_green = False
        assert color in ['red','green'];"factories should be green or red"
        ""
        # BEGIN PROBLEM 2
        """YOUR CODE HERE"""
        # END PROBLEM 2
    
    
    
    
    
    def get_resource(self):
        """
        Creat a list with all the colonies with non-arm but built factories,
        Loop it through,
        add that to the associated variable, print a list of harvest,
        and add the variable to the recource dictionary
        """
        piece = 0
        total = 0 
        
        lst1 = [i for i in ... if ...and...and i.factory_americanized != False] 
        # plz finish the list comprehension before doing the iteration

        # BEGIN PROBLEM 3
        """YOUR CODE HERE"""
        # END PROBLEM 3


        lst2  = self.resource.key()
        lst2.remove(gold)
        for i in lst2:
            total += self.resource[i]
        if total > 10:
            for i in self.resource.keys():
                while self.resource[i] > 0 and total > 10:
                    self.resource[i] -= 1
                    total -= 1
        return self.resource
        





    #  def buy_resource(self):
        ...
    #def build_railway(self,route):
        #...
    #def build_canal(self,place):
        #...
    def build_ship(self,place):
        """

        This function takes in a place object
        and check if the place is in the colony list and has an arm 
        factory and is available to park a ship.
        If so, build the ship there;
        else, build the in the capital.
        Remember that buidling a ship costs money and resources.
        """
        assert place in self.colony ;"The colony should be in the colony list"
        
        # BEGIN PROBLEM 4
        """YOUR CODE HERE"""
        # END PROBLEM 4
    

    def free_colony(self,place,operation='free'):
        assert place in self.colony ;"The colony should be in the colony"
        assert operation in ['free','unfree']; "The operation should be 'free' or 'unfree'"
        if operation == 'free':
            place.no_charge = True
        elif operation == 'unfree':
            place.no_charge = False           

    def exchange_resource(self,opponent,resource,operation,money=0,approved=True):
        """
        This function takes in self, opponent and place, money
        so a place can be exchanged according to the operation. 
        Capitals cannot be exchanged
        """
        assert type(opponent) == Empire; "The opponent must be an empire object"
        assert type(resource) == Resource; "The resource must be a resource object"
        assert operation in ['buy', 'sell']; "Operation can only be buy or sell"
        assert approved == True; "The exchange should be approved"
        assert money >= resource.place; "Insufficient money"
        
        # BEGIN PROBLEM 5A
        """YOUR CODE HERE"""
        # END PROBLEM 5A




    def exchange_colony(self,opponent,place,operation,money=0,approved=True):
        """
        This function takes in self, opponent and place, money
        so a place can be exchanged according to the operation. 
        Capitals cannot be exchanged
        """
        assert type(opponent) == Empire; "The opponent must be an empire object"
        assert type(place) == Colony; "The place must be a colony object"
        assert operation in ['buy', 'sell']; "Operation can only be buy or sell"
        assert approved == True; "The exchange should be approved"
        
        # BEGIN PROBLEM 5B
        """YOUR CODE HERE"""
        # END PROBLEM 5B


    def trancsection(self,opponent,operation,money,approved=True):
        assert type(opponent) == Empire; "The opponent must be an empire object"
        assert operation in ['send','request']; "The place must be a colony object"
        assert approved == True; "The trancsection must be approved"
        if operation == 'send':
            if money <= self.money:
                self.money -= money
                opponent.money += money
                print ("Successful transaction")
            else:
                print("Insufficient fund")
        elif operation == 'request':
            if money <= opponent.money:
                self.money += money
                opponent.money -= money
                print ("Successful transaction")
            else:
                print("Insufficient fund")



    def buy_permit(self,permit):
        """
        This function takes in self and permit
        see if the money is sufficient to buy a permit,
        and see if they already have a same permit in their permit list,
        then give the permit to the buyer by appending it to the permit list
        print  the purchase result by telling them if that was successful
        """
        assert permit in ['junior','senior']; "Permit should be a junior one or a senior one"
        # BEGIN PROBLEM 6
        """YOUR CODE HERE"""
        # END PROBLEM 6



    def trade_start(self,start,end):
        assert type(start) == Colony; "The start place must be a colony"
        assert type(end) == Colony; "The end place must be a colony"
        if self.on_trade:
            return "still trade"
        i = 0
        while self.on_trade == False and i < len(routes):
            if start == trade_start_colony(routes[i]) and end == trade_end_colony(routes[i]):
                self.on_trade = True
                self.money -= 150
                self.route = routes[i]
                return "trade route started!"
            i += 1
        return "could not find route"
    
    def trade_end(self,place):
        """
        ***Notice on Line 25!!!***
        This function takes self and finished place,
        if it matched the trade route, print out the trading information, 
        add the profit into the self`s money, and return the profit
        """
        assert type(place) == Colony; "The place must be a colony object"
        profit = 0

       # BEGIN PROBLEM 7
        """YOUR CODE HERE"""
        # END PROBLEM 7



    def attack(self,enemy,self_point=None,self_ship=None,
               enemy_point=None,enemy_ship=None,enemy_castle=None,self_oil=None,enemy_oil=None):
        assert type(enemy) == Empire; "Enemy must be an Empire"
        assert self_oil in range(3); "Oil use should be fewer than 3"
        assert enemy_oil in range(3); "Oil use should be fewer than 3"
        assert self.resource[oil] >= self_oil; "Insufficient oil"
        assert enemy.resource[oil] >= enemy_oil; "Insufficient oil"
        win = False
        if self_point not in range(1,7) or enemy_point not in range(1,7):
            print  ('dice point should be 1-6')
        elif self_ship > 3:
            print  ('self ship should be less than 3')
        elif enemy_ship > 3:
            print ('enemy ship should be less than 3')
        elif enemy_ship == 2 and enemy_castle:
            print ('enemy ship should be 1 if there`s a castle')
        else:
            enemy_power = enemy.ship * ship_power + enemy.castle * castle_power + enemy_oil
            self_power = self.self_oilship * ship_power + self_oil
            enemy.resource[oil] -= enemy_oil
            self.resource[oil] -= self_oil
            print(self.name + " vs. " + enemy.name)
            print (self.name +': '+self_power)
            print (enemy.name +': '+ enemy_power)
            if  self_power > enemy_power:
                print ('Congrats! You won the battle!')
                win = True
            if self_power == enemy_power:
                print ('try rolling dice again')
            else:
                print ('Sorry! You lost the battle')
        return win
        
        
    def rob(self,enemy,self_point=None,self_ship=None,enemy_point=None
            ,enemy_ship=None,enemy_castle=None,self_oil=None,enemy_oil=None):
        """
        ***Notice Line 25!!!***
        This function determines if you can get something from robbing a ship successfully.
        If you win the battle, and you have a senior permit, you can take over the task
        else if you dont have a senior permit, you get nothing

        is_robber will turn true if you can take over the task
        Return the Colony object of the destination if you get something
        """
        assert type(enemy) == Empire; "Enemy must be an Empire"
        is_robber = False
        destination = None
        permit = 'senior'
        win = self.attack(self,enemy,self_ship=None,self_point=None,
                          enemy_ship=None,enemy_castle=None,enemy_point=None,self_oil=None,enemy_oil=None)
        # BEGIN PROBLEM 8
        """YOUR CODE HERE"""
        # END PROBLEM 8
        self.is_robber = is_robber
        return destination

        
    def trade_end_for_robber(self,place):
        """
        ***Notice Line 25!!!***
        This function is to determine if those who rob and get the trade route successfully can get money 
        when getting to a place where they may want to end the trade route
        
        If the place matches the destination, then the self can get the profit
        else if the place is his own port, or a pirate`s port, then the self can get 150
        otherwise, the self is still on_trade. Return the pro

        To see if a colony is a port, see if its tax is $20 - the feature of ports in this game

        You cannot use the object Pirates in your code since it is not created before this function
        try to match the string name "Pirates" instead
        """
        assert self.robber == True; "Fails when you are not a robber"
        assert type(place) == Colony; "The place must be a colony object"
        
        # BEGIN PROBLEM 9
        """YOUR CODE HERE"""
        # END PROBLEM 9



    def leave_place(self,place):
        assert type(place) == Colony; "The place must be a colony object"
        assert place.has_pandemic == False; "You cannot leave the place with a pandemic"
        ship = "ship_" + self.name
        if ship in place.ships:
            place.ships.remove(ship)
            place.capacity += 1
            print("Successfully left")
        else:
            print("No such ship in the colony")

    def enter_place(self,place,approved=True,no_charge=False):
        """

        This function takes in self and the place where the ship is entering
        It should append the string "ship" + its nationality to the colony ship list,
        If the colony is self`s, there`s no charge for the parking fee, 
        else if the ship is a merchant ship, no charge either,
        otherwise, the colony should charge the ship for parking fee
        If the colony is full, it should refuse ships to enter the colony
        """
        assert type(place) == Colony; "The place must be a colony object"
        permit = 'junior'
        if approved:
            if permit in self.permit:   # the function of a junior permit
                no_charge = True
            # BEGIN PROBLEM 10a
            """YOUR CODE HERE"""
            # END PROBLEM 10a
        else:
            return "The owner refused to let you in"


    def pass_place(self,place,no_charge=False):
        """
        This function is highly similar to the enter_place function,
        but we do not mutate the colony capacity or the ship list of the colony
        So it is possible to pass the colony if the colony is full
        """
        assert type(place) == Colony; "The place must be a colony object"
        permit = 'junior'
        if permit in self.permit:   # the function of a junior permit
            no_charge = True

        # BEGIN PROBLEM 10b
        """YOUR CODE HERE"""
        # END PROBLEM 10b



    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()

class United_Kingdom(Empire):
    def collect_tax(self):
        """
        UK specialist: $10 more per colony 
        >>> uk = United_Kingdom("United_Kongdom",London,british_colonies)
        >>> uk.collect_tax()
        315
        >>> usa = Empire("United_States",New_York,american_colonies)
        >>> uk.colony.append(usa.colony.pop())
        >>> uk.colony.append(usa.colony.pop())
        >>> uk.collect_tax()
        375
        """
        tax = 5
        # BEGIN PROBLEM 11
        """YOUR CODE HERE"""
        # END PROBLEM 11
        if self.double:
            tax *= 2
            self.double = False
        elif self.half:
            tax //= 2
            self.half = False
        return tax


class Russia(Empire):
    """
    Russia specilist: spend either a wood 
    or a metal ticket and $20 to build a factory
    """
    def build_ship(self, place, resource=wood):
        # BEGIN PROBLEM 12
        """YOUR CODE HERE"""
        # END PROBLEM 12


class China(Empire):
    def trade_end(self, place):
        """
        China specilist: $150 extra award when completing a trade route
        """
        # BEGIN PROBLEM 13
        """YOUR CODE HERE"""
        # END PROBLEM 13


class Japan(Empire):
    permit = ['junior'] 
    def enter_place(self, place, no_charge=False, approved=True):
        return super().enter_place(place, True, True)
    def pass_place(self, place, no_charge=False):
        return super().pass_place(place, True)

class Pirates(Empire):
    permit = ['junior','senoir']
    def __init__(self, name=None,capital=None,colony=None):
        self.name = name
        self.capital = capital
        self.colony = colony
        for i in colony:
            self.free_colony(i,"free")
    def exchange_colony(self, opponent, place, operation, money=0, approved=True):
        """
        This function is highly similar to the exchange_colony in Empire class
        but as a pirate you have to make all new colonies no charge 
        """
        # BEGIN PROBLEM 14
        """YOUR CODE HERE"""
        # END PROBLEM 14


class United_States(Empire):
    """
    USA specialist: The United States can build a factory 
    in a colony that does not belong to the United States
    """
    def build_factory(self, place, color):
        # BEGIN PROBLEM 15a
        """YOUR CODE HERE"""
        # END PROBLEM 15a

    def get_resource(self):
        piece = 0
        total = 0 

        # BEGIN PROBLEM 15b
        """YOUR CODE HERE"""
        # END PROBLEM 15b

        lst2  = self.resource.key()
        lst2.remove(gold)
        for i in lst2:
            total += self.resource[i]
        if total > 10:
            for i in self.resource.keys():
                while self.resource[i] > 0 and total > 10:
                    self.resource[i] -= 1
                    total -= 1
        return self.resource
    

    def build_ship(self, place):
        # BEGIN PROBLEM 15c
        """YOUR CODE HERE"""
        # END PROBLEM 15c



class Bank(Empire):
    def __init__(self):
        self.resource = {wood:100000,metal:100000,gold:100000,fertilizer:100000,oil:100000,sugar:100000}


max_turns = 60
def turns(): 
    uk = United_Kingdom("United_Kongdom",London,british_colonies)
    russia = Russia("Russia",Murmansk,russian_colonies)
    china = China("China",Shanghai,chinese_colonies)
    japan = Japan("Japan",Tokyo,japanese_colonies)
    pirates = Pirates("Pirates",Darwin,pirates_colonies)
    usa = United_States("United_States",New_York,american_colonies)
    bank = Empire("Bank")
    empires = [uk,russia,china,japan,pirates,usa]
    news = [pandemic(west_africa),bonus(empires),
            double(empires),half(empires),increased(resources),
            decreased(resources),sink(),oneMore(empires),moveMore()]
    turn = 1
    yield "Game start!"
    while turn <= max_turns:
        yield("Now it`s turn #"+str(turn))
        yield from ["United Kingdom","Russia","China"
                    ,"Japan","Pirates","United States"]
        if turn % 5 == 0:
            
            yield ("***Now it`s tax time***")
            yield ("News:")
           # i = rand(len(news))
           # yield news[i]
            yield ("tax:")
            yield from ["United_Kingdom:", uk.collect_tax(),
                        "Russia:", russia.collect_tax(),
                        "China:", china.collect_tax(),
                        "Japan:", japan.collect_tax(),
                        "Pirates:", pirates.collect_tax(),
                        "United_States:",usa.collect_tax()]
            yield ("resources:")
            yield from [uk.get_resource(),russia.get_resource(),
                        china.get_resource(),japan.get_resource(),
                        pirates.get_resource(),usa.get_resource()]
            yield ("who wants to buy permit? ")

            yield ("Now it's a new era!")

        elif turn == max_turns:
            return 'game over'
        turn += 1

def setup():
    turn = iter(turns())

