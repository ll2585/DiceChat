from .config import *
from .utils import *

class Player():

    def __init__(self, isBot = True):
        self.isBot = isBot
        self.dice = [Dice(), Dice()]
        self.totalscore = 0
        self.rerolled = [False, False]
        self.passed = False
        self.initAttrs()
        self.name = "GENERIC PLAYER"
        
    def roll(self):
        self.passed = False
        for d in self.dice:
            d.roll()
        self.updateAttrs()
	
    def reroll(self, dicenumber):
        assert(dicenumber == 0 or dicenumber == 1)
        #dice number is either 1 or 2. So yo
        self.dice[dicenumber].roll()
        self.rerolled[dicenumber] = True
        self.updateAttrs()
	
    def willReroll(self):
        pass
	
    def getscore(self):
        return self.score

    def endTurn(self):
        self.passed = True
        self.updateAttrs()
        self.rerolled = [False, False]
        totalscore += self.scorethisround
			
    def canReroll(self, dicenumber):
        assert(dicenumber == 0 or dicenumber == 1)
        #dice number is either 1 or 2. So yo
        return not self.rerolled[dicenumber]
     
    def updateAttrs(self):
        if not self.rerolled[0]:
            self.firstdieroll = self.dice[0].face()
            self.firstdiereroll = "Did not reroll"
        else:
            self.firstdiereroll = self.dice[0].face()
            
        if not self.rerolled[1]:
            self.seconddieroll = self.dice[1].face()
            self.seconddiereroll = "Did not reroll"
        else:
            self.seconddiereroll = self.dice[1].face()
            
        self.scorethisround = 0
        for d in self.dice:
            self.scorethisround += d.curface
            
    def initAttrs(self):
        self.firstdieroll = "NA"
        self.firstdiereroll = "NA"
        self.seconddieroll = "NA"
        self.seconddiereroll = "NA"
        self.scorethisround = "NA"
     
    def getturn(self):
        result = "%s/%s" %(self.firstdieroll, self.seconddieroll)
        return result
    
    def diceResults(self):
        return "%s and %s" %(self.dice[0].face(), self.dice[1].face())
    

class HumanPlayer(Player):
    def __init__(self):
        super(HumanPlayer, self).__init__()
        self.name = "Human"
        self.isBot = False
        
class DumbBot(Player):
    def __init__(self):
        super(DumbBot, self).__init__()
        self.name = "DumbBot"
        
