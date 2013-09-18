import random, logging
from .player import *
#from .textinterface import *
#from building import *
import copy

class Game(object):
    def __init__(self, numplayers=2, player_class=Player, singleplayer = False):
        self.sp = singleplayer
        self.num_players = numplayers
        self.players = []
        self.continuous = False
        self.id = None
        self.turn = -1
        self.section = SECTION_DUNGEON
        self.new_section = SECTION_DUNGEON
        self.spaces = SECTION_SPACES[:]
        self.inn_player = None
        self.turn_logs = []
        self.turn_history = []
        self.current_player = None
        
        if singleplayer:
            self.initsp()
        else:
            self.initmp(player_class)
         
    
    def initsp(self):
        bots = []
        numbots = self.num_players - 1
        human = HumanPlayer()
        self.players.append(human)
        for i in range(numbots):
            bots.append(DumbBot())
        self.players += bots
    
    def initmp(numplayers, player_class):
        pass
        '''
        self.num_players = numplayers
        self.players = []
        for i in range(self.num_players):
            player = player_class(self, COLORS[i])
            if self.num_players > 2 and i >= 1:
                player.money += 1
            if i >= 3:
                player.money += 1
            self.players.append(player)
        
        self.continuous = False
        self.id = None
        self.turn = -1
        self.section = SECTION_DUNGEON
        self.new_section = SECTION_DUNGEON
        self.spaces = SECTION_SPACES[:]
        self.inn_player = None

        
        self.special_buildings = special_buildings
        #if players < 3:
        #    self.special_buildings.remove(stables)
        self.normal_buildings = []
        
        random.shuffle(neutral_buildings)
        self.normal_buildings += neutral_buildings
        self.normal_buildings += fixed_buildings
        self.normal_buildings += [NullBuilding("Null")] * 7
        self.normal_buildings += [fixed_gold]
        self.normal_buildings += [NullBuilding("Null")] * 14

        #for b in stone_buildings + wood_buildings:
        #    self.normal_buildings[self.normal_buildings.index(null_building)] = b
        
        
        self.buildings = self.special_buildings + self.normal_buildings
        for building in self.buildings:
            building.owner = None
            
        self.wood_buildings = copy.deepcopy(wood_buildings)
        self.stone_buildings = copy.deepcopy(stone_buildings)
        self.prestige_buildings = copy.deepcopy(prestige_buildings)

        self.bailiff = INITIAL_BAILIFF
        self.provost = INITIAL_BAILIFF

        self.turn_logs = []
        '''

    @property
    def over(self):
        return self.phase == -1
        
    def begin_turn(self):
        self.turn += 1
        self.log('Beginning turn %d' % self.turn)
        self.step = 0
        self.phase = 0
        
    def step_game(self):
        #self.log('STEP_GAME Phase:%d Step:%d' % (self.phase, self.step))
        if self.turn == -1:
            self.begin_turn()
        
        if self.phase == FIRST_ROLL:
            self.current_player = self.players[self.step % self.num_players]
            self.current_player.roll()
            self.loghistory(self.turn, self.current_player)
            self.log('%s rolls %s' %(self.current_player.name, self.current_player.roll))
            self.phase += 1
        if self.phase == WAIT_FOR_REROLL:
            if len([player for player in self.players if not player.passed]) == 0:
                self.phase += 1
                self.step = 0
            else:
                pass
                
    def curPlayerRerolls(self, rerollindex):
        self.current_player.reroll(rerollindex)
        self.loghistory(self.turn, self.current_player)
                
    def getPlayerIndex(self, player):
        i = 0
        for p in self.players:
            if p == player:
                return i
            i += 1

    def loghistory(self, turn, player):
        if len(self.turn_history) <= turn:
            turnhist = [None]*self.num_players
            self.turn_history.append(turnhist)
        self.turn_history[turn][self.getPlayerIndex(player)] = player.getturn()
     
    def log(self, message, player=None, *args):
        if not player:
            rendered =  message
        else:
            rendered = message % ((player.name,) + args)
        logging.getLogger('game').info('[Log][%s]' % self.id + rendered)
        self.turn_logs.append(rendered)