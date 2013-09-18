class Player():
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.isBot = True
        self.canreroll = [False, False]
        self.dice = [0, 0]
        self.olddice = [0, 0]
        self.myTurnOver = True
        self.score = 0

    def roll(self):
        print("I am %s and I AM ROLLIGN WIERJFR" % self.name)
        self.passed = False
        import random
        for i in range(len(self.dice)):
            self.dice[i] = random.randint(1,6)
        self.myTurnOver = False

    def reroll(self, i):
        print("%s is rerolling dice %s" %(self.name, i))
        import random
        for x in range(len(self.dice)):
            self.olddice[x] = self.dice[x]*1
        self.dice[i] = random.randint(1,6)
        self.canreroll[i] = False

    def newTurn(self):
        self.roll()
        self.canreroll = [True, True]

    def turnOver(self):
        print("%s's turn is over" %(self.name))
        self.myTurnOver = True
        self.score += self.dice[0] + self.dice[1]

    def waitingForTurn(self):
        print('i am %s and is my turn over? %s '% (self.name, self.myTurnOver))
        return self.myTurnOver == False


class HumanPlayer(Player):
    def __init__(self, id, name):
        super(HumanPlayer, self).__init__(id, name)
        self.isBot = False
        
class DumbBot(Player):
    def __init__(self, id):
        super(DumbBot, self).__init__(id, "DumbBot")

    def willReroll(self, i):
        import random
        return random.randint(0,1) == 1 and self.canreroll[i]

class HumanWebPlayer(HumanPlayer):
    def __init__(self, cookie):
        super(HumanWebPlayer, self).__init__(self.makeID(cookie), cookie['name'])
        self.isBot = False

    def makeID(self, cookie):
        import gametest.gameutils
        result = gametest.gameutils.make_hash(cookie)
        #print("the hash is %s" %(result))
        return result
        
    def getRollResults(self):
        return "rolled a %s and a %s" %(self.dice[0], self.dice[1])

    def getRerollresults(self, i):
        #print("i is %s and dice is %s and old dice is %s" %(i, self.dice, self.olddice))
        return "rerolled a %s into a %s" %(self.olddice[i], self.dice[i])

class DumbBotWebPlayer(DumbBot):
    def __init__(self, id):
        super(DumbBotWebPlayer, self).__init__(id)

    def getRollResults(self):
        print("i am rolling.")
        return "rolled a %s and a %s" %(self.dice[0], self.dice[1])

    def getRerollresults(self, i):
        #print("i is %s and dice is %s and old dice is %s" %(i, self.dice, self.olddice))
        return "rerolled a %s into a %s" %(self.olddice[i], self.dice[i])