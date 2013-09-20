
class Game(object):

    SCORETHRESHOLD = 100

    def __init__(self):
        self.players = []
        self.curPlayer = None
        self.curPlayerIndex = 0
        self.state = {"players": self.players, "curplayer": self.curPlayer}
        self.turn = 0
        self.started = False


    def getState(self):
        return self.state

    def addPlayer(self, player):
    	self.players.append(player)

    def getPlayerNames(self):
    	result = []
    	for p in self.players:
    		result.append(p.name)

    def nextTurn(self):
        self.turn += 1 
        self.updateCurPlayer()
        self.logturn()
        print("STARTED!")

    def updateCurPlayer(self):
        self.curPlayer = self.players[self.curPlayerIndex]
        #self.curPlayer.newTurn()

    def logturn(self):
        print("it is %s's turn" %self.curPlayer.name)

    def getNumPlayers(self):
        return len(self.players)

    def start(self):
        self.started = True
        self.curPlayer = self.players[self.curPlayerIndex]

    def isStarted(self):
        print("DID I START")
        return self.started

    def waitingForPlayer(self, player):
        for p in self.players:
            if p == player:
                return p.waitingForTurn()


    def curPlayerEndsTurn(self):
        self.curPlayer.turnOver()
        self.curPlayerIndex = (self.curPlayerIndex + 1) % self.getNumPlayers()
        print("cur player ends")


    def gameOver(self):
        for p in self.players:
            if p.score >= Game.SCORETHRESHOLD:
                self.start = False
                return [p.name, p.score]
        return None

    def getScores(self):
        scores = list(zip([p.id for p in self.players], [p.name for p in self.players], [p.score for p in self.players]))
        return scores



class WebGame(Game):
    def __init__(self, id):
        super(WebGame, self).__init__()
        self.id = id
        self.state['id'] = self.id

    def getActivePlayer(self, cookie):
        import gametest.gameutils
        activeplayerID = gametest.gameutils.make_hash(cookie)
        for p in self.players:
            if p.id == activeplayerID:
                return p 

    def isActivePlayerCurPlayer(self, cookie):
        import gametest.gameutils
        activeplayerID = gametest.gameutils.make_hash(cookie)
        return activeplayerID == self.curPlayer.id


    def process(self, action):
        self.messagebody = ""
        if action == 'reroll_1':
            self.curPlayer.reroll(0)
            self.messagebody = self.curPlayer.getRerollresults(0)
        elif action == 'reroll_2':
            self.curPlayer.reroll(1)
            self.messagebody = self.curPlayer.getRerollresults(1)
        elif action == 'end_turn':
            self.curPlayerEndsTurn()
            self.messagebody = "%s ended his turn with a %s and a %s. Total score: %s" %(self.curPlayer.name, self.curPlayer.dice[0], self.curPlayer.dice[1], self.curPlayer.score)
            victor = self.gameOver()
            if victor is None:
                print('no victor, continue')
                self.nextTurn()
            else:
                self.messagebody += "%s wins with a score of %s!" %(victor[0], victor[1])
        elif action == 'start':
            self.messagebody = "has started the game!"
            self.start()
        elif action == 'addBot':
            from gametest.player import DumbBotWebPlayer
            self.addPlayer(DumbBotWebPlayer(0))
            self.messagebody = "has added a bot! Total players: %s" %(self.getNumPlayers())

    def curPlayerBotGo(self):
        message = ""
        p = self.curPlayer
        print("is %s waiting? %s" %(p.name, p.waitingForTurn()))
        assert p.isBot
        if p.didntRollYet():
            print("ok i am goign!!@##$6")
            p.newTurn()
            message = p.getRollResults()
        elif p.willReroll(0):
            p.reroll(0)
            message =  p.getRerollresults(0)
        elif p.willReroll(1):
            p.reroll(1)
            message =  p.getRerollresults(1)
        else:
            self.curPlayerEndsTurn()
            message =  "%s ended his turn with a %s and a %s. Total score: %s" %(p.name, p.dice[0], p.dice[1], p.score)
            victor = self.gameOver()
            if victor is None:
                print('no victor, continue')
                self.nextTurn()
            else:
                self.messagebody += "\n%s wins with a score of %s!" %(victor[0], victor[1])
        return message


    def playerInGame(self, cookie):
        import gametest.gameutils
        toCheck = gametest.gameutils.make_hash(cookie)
        for p in self.players:
            if p.id == toCheck:
                return True
        return False

    def actionResults(self, action):
        return self.messagebody

    def waitingForPlayerCookie(self, cookie):
        import gametest.gameutils
        toCheck = gametest.gameutils.make_hash(cookie)
        for p in self.players:
            if p.id == toCheck:
                tocheck = p
                break
        return self.waitingForPlayer(tocheck)

    def curPlayerID(self):
        print("the current player's id is %s" %(self.curPlayer.id))
        return self.curPlayer.id

    def jsonScores(self):
        scores = self.getScores()
        result = []
        for s in scores:
            temp = {}
            temp['id'] = s[0]
            temp['name'] = s[1]
            temp['score'] = s[2]
            result.append(temp)
        return result