print("***Welcome to ABCDE terminal***")

from Resource_and_Colony_dataBase import *
from trade_route_dataBase import *
from News_function import *

#import random
#n = random.random()


ship_power = 2
castle_power = 3
senior = ['senior','senior']     # original senior permit amount
junior = ['junior','junior','junior']      # original junior permit amount
war = ['war','war','war','war']
tradeEND = ['tradeEND','tradeEND','tradeEND','tradeEND']



class Empire:
    double = False
    half = False
    def __init__(self,name=None,capital=None,colony=[]):
        self.name = name
        self.capital = capital
        self.colony = colony
        self.money = 450
        self.permit = []
        self.on_trade = False
        self.ships = 4
        self.route = None
        self.resource = {wood:5,metal:5,gold:0,sugar:0,fertilizer:0,oil:0}
        self.is_robber = False
   
    ###################################################
    # when using data from trade routes,              # 
    # like its starting points and ending points,     #
    # do not break abstraction barrier! use selectors!#
    ###################################################

    def initial_ship_place(self,p1=None,p2=None,p3=None,p4=None):
        ship = "ship_" + str(self.name)
        print('country: ' + self.name + '\n')
        for i in [p1,p2,p3,p4]:
            if i == None:
                i = self.capital
            if i in self.colony and i.capacity > 0 and self.ships > 0 and i.tax == 20:
                i.ships.append(ship)
                i.capacity -= 1
                self.ships -= 1
                print(i.name + ': ' + "Initialized successfully\n")
            else:
                print(i.name + ': ' + "Unavailable\n")
                if i not in self.colony:
                    print("***place not yours***\n")
                if self.ships <= 0:
                    print("***you have no ships***\n")
                if i.capacity <= 0:
                    print ("***port full***\n")
                

        print("--------------------------")

    def accelerate(self):
        if self.resource[sugar] > 0:
            self.resource[sugar] -= 1
        else:
            return print("Insufficient sugar!")
        
    def collect_tax(self):
        """
        Loop through the colony list of the empire`s, 
        add the tax up and get the total tax.
        
        """
        tax = 5 # $5 bonus for having a capital
        # BEGIN PROBLEM 1
        for i in self.colony:
            tax += i.tax
        # END PROBLEM 1
        if self.double:
            tax *= 2
            self.double = False
        elif self.half:
            tax //= 2
            self.half = False
        self.money += tax
        return tax
    

   
   
   
   
    def build_factory(self,place,color):
        """
        The function takes in self, a colony object and the factory color.
        It should check if the colony is in the list.
        Then see if the colony already has a green or red factory.
        If there is no, spend some amount of resources and money to build one.
        Green factory can be upgraded to a Red factory but we cannot do the opposite.
        
        """
        has_red = False
        has_green = False
        assert color in ['red','green'];"factories should be green or red"
        ""
        # BEGIN PROBLEM 2
        if place not in self.colony:
            return print("This colony does not belong to this empire")
        if place.factory_built:
            if place.is_green:
                has_green = True
            elif place.is_red:
                has_red = True
        if color == 'green':
            if  has_green:
                return print("This colony already has a green factory")  
            elif has_red:
                return print("This colony already has a red factory")  
            elif self.money >= 40 and self.resource[wood] > 0 and self.resource[metal] > 0:  
                place.factory_built = True
                place.is_green = True
                self.money -= 40
                self.resource[wood] -= 1
                self.resource[metal] -= 1
                return print("Successfully built")
            else:
                print("Insufficient resource or money")
        elif color == 'red':
            if has_green and self.resource[wood] > 0:
                place.is_red = True
                self.resource[wood] -= 1
                return print("Successfully built")
            elif has_red:
                return print("This colony already has a red factory")
            elif self.money >= 40 and self.resource[wood] > 1 and self.resource[metal] > 0:
                place.factory_built = True
                place.is_red = True
                self.money -= 40
                self.resource[wood] -= 2
                self.resource[metal] -= 1
                print("Successfully built")
            else:
                return print("Insufficient resource or money")
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
        
        lst1 = [i for i in self.colony if i.resource != arm and i.factory_built == True
                 and i.factory_americanized == False and i.factory_shutdown == False] 
        # plz finish the list comprehension before doing the iteration

        # BEGIN PROBLEM 3
        print ("client: "+self.name)
        for i in resources:
            for j in lst1:
                if j.resource == i:
                    if j.is_red:
                        piece += 2
                    elif j.is_green:
                        piece += 1
            self.resource[i] += piece
            print (i.name+": "+str(piece))
            piece = 0
        print("resource: ")
        # END PROBLEM 3

        # The code below shows resources cannot be more than 10 items except for gold
        lst2  = list(self.resource.keys())
        lst2.remove(gold)
        for i in lst2:
            total += self.resource[i]
        if total > 10:
            for i in self.resource.keys():
                while self.resource[i] > 0 and total > 10:
                    self.resource[i] -= 1
                    total -= 1
        return self.resource



    #def build_railway(self,route):
        #...
    #def build_canal(self,place):
        #...
    def build_ship(self,place):
        """
        This function takes in self and a place object,
        and check if the place is in the colony list and has an arm 
        factory and is available to park a ship.
        If so, build the ship there;
        else, build the in the capital if the colony capacity is not reached.
        Remember that buidling a ship costs money and resources.
        
        """
        assert place in self.colony ;"The colony should be in the colony list"
        assert place.factory_americanized == False; "This is an American factory"
        # BEGIN PROBLEM 4
        if place.capacity <= 0:
            return print("No more space for the new ship")
        elif place.resource != arm and place != self.capital:
            return print("Arm factory is not supported there")
        elif place.factory_built == False and place != self.capital:
            return print("The arm factory is not built")
        elif self.money < 40 or self.resource[wood] < 1 or self.resource[metal] < 1:
            return print("Insufficient resource or money")
        self.ships += 1
        self.money -= 40
        self.resource[wood] -= 1
        self.resource[metal] -= 1
        place.capacity -= 1
        place.ships.append("ship_"+self.name)
        return print("Successfully built")
        # END PROBLEM 4
    


    def free_colony(self,place,operation='free'):
        assert place in self.colony ;"The colony should be in the colony"
        assert operation in ['free','unfree']; "The operation should be 'free' or 'unfree'"
        if operation == 'free':
            place.no_charge = True
        elif operation == 'unfree':
            place.no_charge = False  
        return print("Successful operation")  
    
    def shut_down(self,place,operation='disrupt'):
        assert operation in ['disrupt','restart']; "operation should be restart or disrupt"
        assert place.factory_built == True; "the place does not have factory"
        can_do = False
        if self.name == "United_States" and place.factory_americanized == True:
            can_do = True
        elif place in self.colony:
            can_do = True
        if can_do:
            if operation == 'disrupt':
                place.factory_shutdown = True
            elif operation == 'restart':
                place.factory_shutdown = False
            return print("Successful operation")
        else:
            return print("Fails because you do not have the right to do that.")


    def exchange_resource(self,opponent,resource,operation,money=0,approved=True):
        """
        This function takes in self, opponent and resource, money,
        so a place can be exchanged according to the operation.
        
        """
        # assert type(opponent) == Empire; "The opponent must be an empire object"
        assert type(resource) == Resource; "The resource must be a resource object"
        assert operation in ['buy', 'sell']; "Operation can only be buy or sell"
        assert approved == True; "The exchange should be approved"
        if money > self.money:
            return print("Insufficient money")
        if opponent.name == 'Bank':
            if operation == 'buy':
                money = resource.price + 5
            if operation == 'sell':
                money = resource.price - 5
        # BEGIN PROBLEM 5A
        if operation == 'buy':
            if opponent.resource[resource] < 1:
                return print("Insufficient resource")
            elif self.money < money:
                return print("Insufficient money")
            else:
                self.resource[resource] += 1
                self.money -= money
                opponent.resource[resource] -= 1
                opponent.money += money
                print("Successfully exchanged")
        elif operation == 'sell':
            if self.resource[resource] < 1:
                return print("Insufficient resource")
            elif opponent.money < money:
                return print("Insufficient money")
            else:
                opponent.resource[resource] += 1
                opponent.money -= money
                self.resource[resource] -= 1
                self.money += money
                print("Successfully exchanged")

        # END PROBLEM 5A




    def exchange_colony(self,opponent,place,operation,money=0,approved=True):
        """
        This function takes in self, opponent and place, money
        so a place can be exchanged according to the operation. 
        Capitals cannot be exchanged
        
        """
        #assert type(opponent) == Empire; "The opponent must be an empire object"
        assert type(place) == Colony; "The place must be a colony object"
        assert operation in ['buy', 'sell']; "Operation can only be buy or sell"
        assert approved == True; "The exchange should be approved"
        
        # BEGIN PROBLEM 5B
        if place == self.capital or place == opponent.capital:
            return print("Capital cannot be exchanged")
        if operation == 'buy':
            if self.money < money:
                return print("Insufficient fund")
            elif place not in opponent.colony:
                return print("The opponent does not have this place")
            else:
                self.colony.append(place)
                self.money -= money
                opponent.colony.remove(place)
                opponent.money += money
                place.no_charge = False
                place.owner = self.name
                print("Successful transaction")
        elif operation == 'sell':
            if opponent.money < money:
                return print("Insufficient fund")
            elif place not in self.colony:
                return print("The self does not have this place")
            else:
                opponent.colony.append(place)
                opponent.money -= money
                self.colony.remove(place)
                self.money += money
                place.no_charge = False
                place.owner = opponent.name
                print("Successful transaction")
        # END PROBLEM 5B



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
        if permit in self.permit:
            return print("There is alreay one same permit in the permit list")
        else:
            if permit == "junior":
                if len(junior) <= 0:
                    return print("This permit is sold out")
                elif self.money < 50:
                    return print("Insufficient fund")
                else:
                    self.money -= 50
                    self.permit.append(junior.pop())
                    return print("Successful purchase")
            elif permit == "senior":
                if len(senior) <= 0:
                    return print("This permit is sold out")
                elif self.money < 100:
                    return print("Insufficient fund")
                else:
                    self.money -= 100
                    self.permit.append(senior.pop())
                    return print("Successful purchase")
        # END PROBLEM 6

    def exchange_permit(self,opponent,permit,operation,money=0,approved=True):
        # assert type(opponent) == Empire; "Opponent should be an Empire"
        assert permit in ['junior','senior']; "Permit should be junior or senior"
        assert approved == True; "Purchase should be approved"
        assert operation in ['buy','sell']; "Operation should be buy or sell"
        if operation == 'buy':
            if permit not in self.permit and permit in opponent.permit:
                self.money -= money
                self.permit.append(permit)
                opponent.money += money
                opponent.permit.remove(permit)
            else:
                return print("Fail purchase")
        elif operation == 'sell':
            if permit not in opponent.permit and permit in self.permit:
                self.money += money
                self.permit.removed(permit)
                opponent.money -= money
                opponent.permit.append(permit)
            else:
                return print("Fail purchase")



    def ship_in_place(self,place):
        ship = "ship_" + self.name
        return ship in place.ships


    def trade_start(self,start,end):
        assert type(start) == Colony; "The start place must be a colony"
        assert type(end) == Colony; "The end place must be a colony"
        assert self.on_trade == False; "still trade"
        if not self.ship_in_place(start):
            return print("enter the place first")
        i = 0
        while self.on_trade == False and i < len(routes):
            if start == trade_start_colony(routes[i]) and end == trade_end_colony(routes[i]):
                self.on_trade = True
                self.money -= 150
                self.route = routes[i]
                print("trade route started!")
                print("start: ")
                return start

            i += 1
        return print("could not find route")
    
    def trade_end(self,place):
        """
        ***Notice on Line 36!!!***
        This function takes self and finished place,
        if it matched the trade route, print out the trading information, 
        add the profit into the self`s money, and return the profit. 
        At the same time, the resource price will drop by $5 for the first
        4 trade-ends for every 5 times (will be renewed every tax time), 
        AS LONG AS the price did not hit the lowest price.
        
        """
        assert type(place) == Colony; "The place must be a colony object"
        profit = 0
        if not self.ship_in_place(start):
            return print("enter the place first")
       # BEGIN PROBLEM 7
        if place != trade_end_colony(self.route):
            return print("The destination does not match the trade route!")
        else:
            start = trade_start_colony(self.route)
            end = trade_end_colony(self.route)
            profit = trade_profit(self.route)
            self.on_trade = False
            self.route = None
            self.money += profit
            print("Congrats! You completed the trade route!")
            print("merchant: " + self.name)
            print("start: " + start.name)
            print("end: " + end.name)
            print("profit: ")
            if len(tradeEND) > 0:
                for i in resources:
                    if i.price >= i.lowest_price + 5:
                        i.price -= 5
                tradeEND.pop()
        # END PROBLEM 7

        return profit



    def attack(self,enemy,self_point=0,self_ship=0,
               enemy_point=0,enemy_ship=0,castle=None,self_oil=0,enemy_oil=0):
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
        elif enemy_ship == 2 and castle == None:
            print ('enemy ship should be 1 if there`s a castle')
        else:
            if castle:
                enemy_power = enemy_point * (enemy_ship * ship_power + castle.quantity * castle_power) + enemy_oil
            else:
                enemy_power = enemy_point * (enemy_ship * ship_power) + enemy_oil
            self_power = self_point * (self_ship * ship_power) + self_oil
            enemy.resource[oil] -= enemy_oil
            self.resource[oil] -= self_oil
            print(self.name + " vs. " + enemy.name)
            print (self.name +': '+ str(self_power))
            print (enemy.name +': '+ str(enemy_power))
            if  self_power > enemy_power:
                enemy.ships -= enemy_ship
                if castle:
                    word = "ship" + str(enemy.name)
                    for i in range(enemy_ship):
                        if word in castle.ships:
                            castle.ship.remove(word)
                            i = enemy_ship
                if len(war) > 0:
                    for i in resources: #resource prices are increased by $10 for every war for the first 4 wars
                        i.price += 10
                    war.pop()
                print ('Congrats! You won the battle!')
                win = True
            elif self_power == enemy_power:
                print ('try rolling dice again')
            else:
                self.ships -= self_ship
                print ('Sorry! You lost the battle')
                if len(war) > 0:
                    for i in resources: #resource prices are increased by $10 for every war for the first 4 wars
                        i.price += 10
                    war.pop()
        return win
        
        
    def rob(self,enemy,self_point=0,self_ship=0,enemy_point=0
            ,enemy_ship=0,castle=None,self_oil=0,enemy_oil=0):
        """
        ***Notice Line 36!!!***
        This function determines if you can get something from robbing a ship successfully.
        If you win the battle, and you have a senior permit, you can take over the task,
        else if you dont have a senior permit, you get nothing.

        is_robber will turn true if you can take over the task
        Return the Colony object of the destination if you get something
        
        """
        # assert type(enemy) == Empire; "Enemy must be an Empire"
        is_robber = False
        destination = None
        permit = 'senior'
        win = self.attack(enemy,self_point,self_ship,
                          enemy_point,enemy_ship,castle,self_oil,enemy_oil)
        # BEGIN PROBLEM 8
        if win != True:
            return
        route = enemy.route
        enemy.route = None
        enemy.on_trade = False
        if permit not in self.permit:
            return print("But you get nothing because you don`t have a senior permit")
        print ("You have a senior permit, awesome! You are on trade now!")
        print("The Destination is: ")
        self.route = route
        self.on_trade = True
        is_robber = True
        destination = trade_end_colony(self.route)
        # END PROBLEM 8
        self.is_robber = is_robber
        return destination

        
    def trade_end_for_robber(self,place):
        """
        ***Notice Line 36!!!***
        This function is to determine if those who rob and get the trade route successfully can get money 
        when getting to a place where they may want to end the trade route.
        
        If the place matches the destination, then the self can get the profit.
        Else if the place is his own port, or a pirate`s port, then the self can get 150.
        Otherwise, the self is still on_trade. Return the profit.

        To see if a colony is a port, see if its tax is $20 - the feature of ports in this game.

        You cannot use the object Pirates in your code since it is not created before this function
        try to match the string name "Pirates" instead.
        
        """
        assert self.is_robber == True; "Fails when you are not a robber"
        assert type(place) == Colony; "The place must be a colony object"
        
        # BEGIN PROBLEM 9
        eligible = False
        reached = False
        if place == trade_end_colony(self.route):
            eligible, reached = True,True
        if place in self.colony or place.owner == "Pirates":
            eligible = True
        if place.tax != 20:
            eligible, reached = False,False
        if eligible:
            profit = 150
            route = self.route
            self.route = None
            self.on_trade = False
            self.is_robber = False
            print("Congrats! You completed the trade route!")
            print("robber: " + self.name)
            print("end: " + place.name)
            print("profit:")
            if reached:
                profit = trade_profit(route)
            self.money += profit
            return profit
        else:
            return print("This is not a suitable destination!")
            

            

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
            print("No such a ship in the colony")

    def enter_place(self,place,is_merchant=False,no_charge=False,approved=True):
        """
        This function takes in self and the place where the ship is entering
        It should append the string "ship_" + its nationality to the colony ship list,
        If the colony is self`s, there`s no charge for the parking fee, 
        else if the ship is a merchant ship, no charge either,
        otherwise, the colony should charge the ship for parking fee.
        If the colony is full, it should refuse ships to enter the colony
        
        """
        assert type(place) == Colony; "The place must be a colony object"
        assert approved == True;"The owner refused to let you in"
        permit = 'junior'
        if permit in self.permit:   # the function of a junior permit
            no_charge = True
        if self.name == "United_States" and place.factory_americanized == True:
            no_charge = True

        # BEGIN PROBLEM 10A
        if is_merchant:
            no_charge = True
        if place.capacity <= 0:
            return print("The colony is full")
        if place in self.colony:
            no_charge = True
        if no_charge or place.no_charge:
            place.capacity -= 1
            place.ships.append("ship_" + self.name)
            return print("Successfully entered")
        else:
            if self.money >= place.fee:
                if place not in self.colony:
                    for i in empires:
                        if i.name == place.owner:
                            i.money += place.fee
                self.money -= place.fee
                place.capacity -= 1
                place.ships.append("ship_" + self.name)
                return print("Successfully entered")
            else: 
                return print("Insufficient Fund")
        # END PROBLEM 10A

        



    def pass_place(self,place,is_merchant=False,no_charge=False):
        """
        This function is highly similar to the enter_place function,
        but we do not mutate the colony capacity or the ship list of the colony.
        So it is possible to pass the colony if the colony is full
        
        """
        assert type(place) == Colony; "The place must be a colony object"
        permit = 'junior'
        if permit in self.permit:   # the function of a junior permit
            no_charge = True
        if self.name == "United_States" and place.factory_americanized == True:
            no_charge = True
        
        # BEGIN PROBLEM 10B
        if is_merchant:
            no_charge = True
        if place in self.colony:
            no_charge = True
        if no_charge or place.no_charge:
            return print("Successfully passed")
        else:
            if self.money >= place.fee:
                if place not in self.colony:
                    for i in empires:
                        if i.name == place.owner:
                            i.money += place.fee
                self.money -= place.fee
                return print("Successfully passed")
            else: 
                return print("Insufficient Fund")
        # END PROBLEM 10B



    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()

class United_Kingdom(Empire):
    def __init__(self,name=None,capital=None,colony=[]):
        super().__init__(name,capital,colony)
    def collect_tax(self):
        """
        UK specialist: $10 more per colony 
        
        """
        tax = 5
        # BEGIN PROBLEM 11
        for i in self.colony:
            tax += i.tax
            tax += 10
        # END PROBLEM 11
        if self.double:
            tax *= 2
            self.double = False
        elif self.half:
            tax //= 2
            self.half = False
        self.money += tax
        return tax


class Russia(Empire):
    def __init__(self,name=None,capital=None,colony=[]):
        super().__init__(name,capital,colony)
    def build_ship(self, place, resource=wood):
        """
        Russia specilist: spend either a wood 
        or a metal ticket and $20 to build a ship
        
        """
        # BEGIN PROBLEM 12
        if place.capacity <= 0:
            return print("No more space for the new ship")
        elif place.resource != arm and place != self.capital:
            return print("Arm factory is not supported there")
        elif place.factory_built == False and place != self.capital:
            return print("The arm factory is not built")
        elif self.money < 40 or self.resource[wood] < 1 or self.resource[metal] < 1:
            return print("Insufficient resource and/or money")
        self.ships += 1
        self.money -= 20
        self.resource[resource] -= 1
        place.capacity -= 1
        place.ships.append("ship_"+self.name)
        return print("Successfully built")
        # END PROBLEM 12


class China(Empire):
    def __init__(self,name=None,capital=None,colony=[]):
        super().__init__(name,capital,colony)
    def trade_end(self, place):
        """
        China specilist: $150 extra award when completing a trade route
        """
        # BEGIN PROBLEM 13
        if place != trade_end_colony(self.route):
            return print("The destination does not match the trade route!")
        else:
            start = trade_start_colony(self.route)
            end = trade_end_colony(self.route)
            profit = trade_profit(self.route)
            self.on_trade = False
            self.route = None
            self.money += profit
            self.money += 150
            print("Congrats! You completed the trade route!")
            print("merchant: " + self.name)
            print("start: " + start.name)
            print("end: " + end.name)
            print("profit: ")
            for i in resources:
                if i.price >= i.lowest_price + 5 and len(tradeEND) > 0:
                    i.price -= 5
            tradeEND.pop()
            return profit
        # END PROBLEM 13


class Japan(Empire):
    def __init__(self,name=None,capital=None,colony=[]):
        super().__init__(name,capital,colony)
    permit = ['junior'] 
    def enter_place(self, place, no_charge=False, approved=True):
        return super().enter_place(place, True, True)
    def pass_place(self, place, no_charge=False):
        return super().pass_place(place, True)

class Pirates(Empire):
    permit = ['junior','senoir']
    def __init__(self,name=None,capital=None,colony=[]):
        super().__init__(name,capital,colony)
        for i in self.colony:
            i.no_charge = True
    def exchange_colony(self, opponent, place, operation, money=0, approved=True):
        """
        """
        # BEGIN PROBLEM 14
        if place == self.capital or place == opponent.capital:
            return print("Capital cannot be exchanged")
        if operation == 'buy':
            if self.money < money:
                return print("Insufficient fund ")
            elif place not in opponent.colony:
                return print("The opponent does not have this place")
            else:
                self.colony.append(place)
                self.money -= money
                opponent.colony.remove(place)
                opponent.money += money
                place.no_charge = True
                place.owner = self.name
                print("Successful transaction")
        elif operation == 'sell':
            if opponent.money < money:
                return print("Insufficient fund")
            elif place not in self.colony:
                return print("The self does not have this place")
            else:
                opponent.colony.append(place)
                opponent.money -= money
                self.colony.remove(place)
                self.money += money
                place.no_charge = False
                place.owner = opponent.name
                print("Successful transaction")
        # END PROBLEM 14


class United_States(Empire):
    """
    USA specialist: The United States can build a factory 
    in a colony that does not belong to the United States
    """
    def __init__(self,name=None,capital=None,colony=[]):
        super().__init__(name,capital,colony)
    def build_factory(self, place, color):
        """
        
        """
        # BEGIN PROBLEM 15A
        has_red = False
        has_green = False
        assert color in ['red','green']; "factories should be green or red"
        if place.factory_built:
            if place.is_green:
                has_green = True
            elif place.is_red:
                has_red = True
        if color == 'green':
            if  has_green:
                return print("This colony already has a green factory")  
            elif has_red:
                return print("This colony already has a red factory")  
            elif self.money >= 40 and self.resource[wood] > 0 and self.resource[metal] > 0:  
                place.factory_built = True
                place.factory_americanized = True
                place.is_green = True
                self.money -= 40
                self.resource[wood] -= 1
                self.resource[metal] -= 1
                return print("Successfully built")
            else:
                print("Insufficient resource or money")
        elif color == 'red':
            if has_green and self.resource[wood] > 0:
                place.is_red = True
                place.factory_americanized = True
                self.resource[wood] -= 1
                return print("Successfully built")
            elif has_red:
                return print("This colony already has a red factory")
            elif self.money >= 40 and self.resource[wood] > 1 and self.resource[metal] > 0:
                place.factory_built = True
                place.factory_americanized = True
                place.is_red = True
                self.money -= 40
                self.resource[wood] -= 2
                self.resource[metal] -= 1
                return print("Successfully built")
            else:
                return print("Insufficient resource or money")
        # END PROBLEM 15A

    def get_resource(self):
        """
        
        """
        piece = 0
        total = 0 

        # BEGIN PROBLEM 15B
        lst1 = [i for i in not_arm_colonies if i.factory_shutdown == False and i.factory_americanized == True] 
        print ("client: "+self.name)
        for i in resources:
            for j in lst1:
                if j.resource == i:
                    if j.is_red:
                        piece += 2
                    elif j.is_green:
                        piece += 1
            self.resource[i] += piece
            print (i.name+": "+str(piece))
            piece = 0
        print("resource: ")
        # END PROBLEM 15B

        lst2  = [wood,metal,fertilizer,sugar,oil]
        for i in lst2:
            total += self.resource[i]
        if total > 10:
            for i in lst2:
                while self.resource[i] > 0 and total > 10:
                    self.resource[i] -= 1
                    total -= 1
        return self.resource
    

    def build_ship(self, place):
        """
        
	    """
        # BEGIN PROBLEM 15C
        assert place.factory_americanized == True; "This is America building ships"
        if place.capacity <= 0:
            return print("No more space for the new ship")
        elif place.resource != arm and place != self.capital:
            return print("Arm factory is not supported there")
        elif place.factory_built == False and place != self.capital:
            return print("The arm factory is not built")
        elif self.money < 40 or self.resource[wood] < 1 or self.resource[metal] < 1:
            return print("Insufficient resource or money")
        self.ships += 1
        self.money -= 40
        self.resource[wood] -= 1
        self.resource[metal] -= 1
        place.capacity -= 1
        place.ships.append("ship_"+self.name)
        return print("Successfully built")
        # END PROBLEM 15C



class Bank(Empire):
    def __init__(self):
        self.resource = {wood:100000,metal:100000,gold:100000,fertilizer:100000,
                         oil:100000,sugar:100000}


uk = United_Kingdom("United_Kingdom",London,british_colonies)
russia = Russia("Russia",Murmansk,russian_colonies)
china = China("China",Shanghai,chinese_colonies)
japan = Japan("Japan",Tokyo,japanese_colonies)
pirates = Pirates("Pirates",Darwin,pirates_colonies)
usa = United_States("United_States",New_York,american_colonies)
bank = Empire("Bank")
empires = [uk,russia,china,japan,pirates,usa]

test = True
if test == True:
    uk.initial_ship_place(british_colonies[1],british_colonies[4],british_colonies[3])
    russia.initial_ship_place(russian_colonies[1],russian_colonies[4],russian_colonies[3])
    china.initial_ship_place(chinese_colonies[1],chinese_colonies[4],chinese_colonies[3])
    japan.initial_ship_place(japanese_colonies[1],japanese_colonies[4],japanese_colonies[3])
    pirates.initial_ship_place(pirates_colonies[1],pirates_colonies[4],pirates_colonies[3])
    usa.initial_ship_place(american_colonies[4],american_colonies[1],american_colonies[3])

max_turns = 60
def turns(): 
    
    #news = [pandemic(west_africa),bonus(empires),
     #       double(empires),half(empires),increased(resources),
      #      decreased(resources),sink(),oneMore(empires),moveMore()]
    turn = 1
    #if turn == 1:
    #    print ("Game start!")
    while turn <= max_turns:
        yield print("Now it`s turn #"+str(turn))
        yield print("United Kingdom")
        yield print("Russia")
        yield print("China")
        yield print("Japan")
        yield print("Pirates")
        yield print("United States")
        if turn % 5 == 0:
            
            """BEGIN PROBLEM 16"""
            war = ['war', 'war', 'war', 'war']
            tradeEND = ['tradeEND', 'tradeEND', 'tradeEND', 'tradeEND']
            yield print("***Now it`s tax time***")
            yield print("News:");print("--------------------")
            #i = n % len(news)
            #yield news[i]
            print("--------------------")
            yield print("tax:")
            print("--------------------")
            print("United_Kingdom: "+str(uk.collect_tax()))
            print("Russia: "+str(russia.collect_tax()))
            print("China: "+str(china.collect_tax()))
            print("Japan: "+str(japan.collect_tax()))
            print("Pirates: "+str(pirates.collect_tax()))
            print("United_States: "+str(usa.collect_tax()))
            print("--------------------")
            
            yield print("resources:");print("--------------------")
            yield print(uk.get_resource());print("---------------------------------")
            yield print(russia.get_resource());print("---------------------------------")
            yield print(china.get_resource());print("---------------------------------")
            yield print(japan.get_resource());print("---------------------------------")
            yield print(pirates.get_resource());print("---------------------------------")
            yield print(usa.get_resource());print("---------------------------------")
            yield print("who wants to buy permit? ")

            yield print("Now it's a new era!")

            """BEGIN PROBLEM 16"""
        if turn >= max_turns:
            return print('game over')
        turn += 1

turn = iter(turns())