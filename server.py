import logging
import tornado.auth
import tornado.escape
import tornado.ioloop
import tornado.web
import os.path
import uuid

from game.serialize import game_to_json
from game.game import Game
from gametest.game import Game, WebGame
from gametest.player import HumanWebPlayer, DumbBot, DumbBotWebPlayer
from tornado import gen
from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

GAMES = {}


class MessageBuffer(object):
    def __init__(self):
        self.waiters = set()
        self.cache = []
        self.cache_size = 200


    def wait_for_messages(self, callback, cursor=None):
        if cursor:
            new_count = 0
            for msg in reversed(self.cache):
                if msg["id"] == cursor:
                    break
                new_count += 1
            if new_count:
                callback(self.cache[-new_count:])
                return
        print('waiting')
        self.waiters.add(callback)

    def cancel_wait(self, callback):
        self.waiters.remove(callback)

    def new_messages(self, messages):
        logging.info("Sending new message to %r listeners", len(self.waiters))
        for callback in self.waiters:
            try:
                callback(messages)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        print('removing waiters')
        self.waiters = set()
        self.cache.extend(messages)
        #print(self.cache)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]


# Making this a non-singleton is left as an exercise for the reader.
global_message_buffer = MessageBuffer()

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("chatdemo_user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("index.html", messages=global_message_buffer.cache)

class TestHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.gameIdProvided:
            gameid = self.get_argument("id")
        else:
            import random
            gameid = random.randint(1000000,9999999)
        if gameDoesNotExistYet(gameid):
            makeNewGame(gameid)
        curGame = GAMES[gameid]
        me = makeReferenceToMe(self)

        if thisPlayerIsNotInTheGame(curGame, me):
            if not gameStarted(curGame):
                joinGame(curGame, me)
                self.sendPlayerJoinedGameMessage(curGame, me)
                curGame.nextTurn()
            else:
                print("game started too bad")
        self.render("gameindex.html", eventmessages=global_message_buffer.cache, g = curGame, activePlayerCurPlayer = curGame.isActivePlayerCurPlayer(myID(self)), id = gameid)

    def gameIdProvided(self):
        #self.get_arguments returns a list of the arguments with the given name.
        #If the argument is not present, returns an empty list.
        print(self.get_arguments("id"))
        return len(self.get_arguments("id")) != 0

    def sendPlayerJoinedGameMessage(self, game, player):
        import gametest.gameutils
        joinmessage ={
                "id": str(uuid.uuid4()),
                "from": player['name'],
                "event_type": "firstroll",
                "body": "joined the game. Total players: %s" %(game.getNumPlayers()),
                "players_in_game": game.getNumPlayers(),
                "gameid": game.id,
                "player_joined": True,
                "joinername": player['name'],
                "joinerid": gametest.gameutils.make_hash(player),
                #CHANGE THIS MAYBE?
                "joinerscore": 0
            }
        joinmessage["html"] = tornado.escape.to_basestring(
            self.render_string("eventmessage.html", message=joinmessage))
        sendmessage(joinmessage)

def gameStarted(game):
    return game.started

def gameDoesNotExistYet(gameid):
    return gameid not in GAMES

def makeNewGame(gameid):
    GAMES[gameid] = WebGame(gameid)

def makeReferenceToMe(handler):
    return myID(handler)

def thisPlayerIsNotInTheGame(game, player):
    return not game.playerInGame(player)

def joinGame(game, player):
    game.addPlayer(HumanWebPlayer(player))



class MessageNewHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        message = {
            "id": str(uuid.uuid4()),
            "from": self.current_user["name"],
            "body": self.get_argument("body"),
        }
        # to_basestring is necessary for Python 3's json encoder,
        # which doesn't accept byte strings.
        message["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=message))
        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)
        global_message_buffer.new_messages([message])

#called when I submit something
class ActionEventHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):

        gameid = self.get_argument("gameid")
        try:
            self.curGame = GAMES[gameid]
        except KeyError:
            print("There was an error, did games disappear? %s" %GAMES)
        #make a message, which is just me sending my event
        #this is horribly coded please change this sometime
        message = self.processargs()


        # to_basestring is necessary for Python 3's json encoder,
        # which doesn't accept byte strings.
        message["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=message))
        if self.get_argument("next", None):
            print('redirecting to %s ' %self.get_argument("next"))
            self.redirect(self.get_argument("next"))
        else:
            #write json if not redirecting
            print("we are writing %s" %message)
            self.write(message)
        #append it to the asyncher
        global_message_buffer.new_messages([message])

        #bandage hack to make other player go
        if self.curGame.started:
            if not self.curGame.curPlayer.isBot and self.curGame.curPlayer.didntRollYet():
                self.humanMakesFirstRoll()

            while self.curGame.curPlayer.isBot:
                curBot = self.curGame.curPlayer
                botname = curBot.name
                botaction = self.curGame.curPlayerBotGo()
                newmessage ={
                    "id": str(uuid.uuid4()),
                    "from": curBot.name,
                    "event_type": botaction,
                    "body": botaction,
                    "gameid": gameid
                }
                newmessage["html"] = tornado.escape.to_basestring(
                    self.render_string("message.html", message=newmessage))
                if self.curGame.action is Game.ACTION_ENDTURN:
                    newmessage['scores'] = dict(scoreboard=self.curGame.jsonScores())
                sendmessage(newmessage)
                print('sent message %s' %newmessage)
                print("ok it sent check if i am cur player %s" %(self.curGame.curPlayer))
                thename = self.curGame.curPlayer.name
                if not self.curGame.curPlayer.isBot  and self.curGame.curPlayer.didntRollYet():
                    self.humanMakesFirstRoll()

    def checkForMyTurn(self):
        self.humanMakesFirstRoll()

    def humanMakesFirstRoll(self):
        gameid = self.get_argument("gameid")
        #if self.curGame.isActivePlayerCurPlayer(myID(self)):
        print("OK humans turn actually its %s turn" %(self.curGame.curPlayer.name))
        self.curGame.curPlayer.newTurn()
        humanmessage ={
                "id": str(uuid.uuid4()),
                "from": self.curGame.curPlayer.name,
                "event_type": "ok",
                "body": self.curGame.curPlayer.getRollResults(),
                "dice1": self.curGame.curPlayer.dice[0],
                "dice2": self.curGame.curPlayer.dice[1],
                "current_player": self.curGame.curPlayer.name,
                "gameid": gameid
            }
        humanmessage["html"] = tornado.escape.to_basestring(
                self.render_string("message.html", message=humanmessage))
        print("the current player is %s" %(self.curGame.curPlayer))
        humanmessage['currentPlayer'] = self.curGame.curPlayerID()
        print('sending new message %s' %humanmessage)
        sendmessage(humanmessage)

    def processargs(self):
        message = {
            "id": str(uuid.uuid4()),
            "from": self.current_user["name"],
            "event_type": self.get_argument("action"),
            "body": "OK",
            "gameid": self.get_argument("gameid")
        }
        if self.get_argument("action"):
            action = self.get_argument('action')
            self.curGame.process(action)
            if action == 'reroll_1':
                message['rerolled1'] = True
                print("pressed reroll1")
            elif action == 'reroll_2':
                message['rerolled2'] = True
                print("pressed reroll2")
            elif action == 'end_turn':
                message['waiting'] = True
                message['scores'] = dict(scoreboard=self.curGame.jsonScores())
                #print("the game is %s" %(self.curGame.players[0].name))
                print("pressed end")
            elif action == 'start':
                message['started'] = True
                print("start game!")
            elif action == 'addBot':
                message['addBot'] = True
                message['player_joined'] = True
                #CHANGE THIS TO BE DYNAMIC!!
                message['joinername'] = "DumbBot"
                message['joinerid'] = 0
                message['joinerscore'] = 0
                print("ADDED BOT!")
            if action == 'start':
                pass
                #self.checkForMyTurn()
            message['body'] = self.curGame.actionResults(action)
            if self.curGame.gameOver() is not None:
                message['gameover'] = True
        print(self.request.arguments)

        message['players_in_game'] = self.curGame.getNumPlayers()
        return message


class ActionUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self):
        cursor = self.get_argument("cursor", None)
        global_message_buffer.wait_for_messages(self.on_new_messages,
                                                cursor=cursor)

    def on_new_messages(self, messages):
        # Closed client connection
        #called when I receieve messages
        print('receieved messages %s' %messages)
        messages = self.processEvent(messages)
        if self.request.connection.stream.closed():
            return
        #print("le finish with the dict %s" %dict(messages=messages))
        self.finish(dict(messages=messages))

    def processEvent(self, messages):
        gameid = messages[0]['gameid']
        self.curGame = GAMES[gameid]
        print("the cur player is %s" %self.curGame.curPlayer.name)
        if 'joinername' in messages[0]:
            messages[0]['other_player_joined'] = messages[0]['joinername'] != me(self)
        if 'current_player' in messages[0]:
            messages[0]['waitingforme'] = messages[0]['current_player'] == me(self)
        #messages[0]['waitingforme'] = self.curGame.waitingForPlayerCookie(myID(self))
        return messages

    def on_connection_close(self):
        global_message_buffer.cancel_wait(self.on_new_messages)

class MessageUpdatesHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self):
        cursor = self.get_argument("cursor", None)
        global_message_buffer.wait_for_messages(self.on_new_messages,
                                                cursor=cursor)

    def on_new_messages(self, messages):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(dict(messages=messages))

    def on_connection_close(self):
        global_message_buffer.cancel_wait(self.on_new_messages)

class AuthLoginHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        self.render("login.html")

    def post(self):
        user = {'name': self.get_argument('name')}
        self.set_secure_cookie("chatdemo_user", tornado.escape.json_encode(user))
        self.redirect("/")


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("chatdemo_user")
        self.write("You are now logged out")

class LoadHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        print(self.get_argument("load_find"))
        import gametest.gameutils
        activeplayerID = gametest.gameutils.make_hash(myID(self))
        response = { "activeplayerID": activeplayerID}
        print('sending id %s' %response)
        self.write(response)
        #in case i ever need to run something on load
        '''
        gameid = self.get_argument("gameid")
        newmessage ={
                        "id": str(uuid.uuid4()),
                        "from": "me",
                        "event_type": "ok",
                        "body": "your turn bro",
                        "gameid": gameid
                    }
        newmessage["html"] = tornado.escape.to_basestring(
                        self.render_string("message.html", message=newmessage))
        sendmessage(self, newmessage)
        '''

def me(self):
    return tornado.escape.json_decode(self.get_secure_cookie("chatdemo_user"))['name']


def myID(self):
    return tornado.escape.json_decode(self.get_secure_cookie("chatdemo_user"))


def sendmessage(message, numseconds = .5):
    import datetime
    tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=numseconds), callback = lambda: lambdafunction())

    def lambdafunction():
        #handler.write(message)
        global_message_buffer.new_messages([message])

    print("new message sent")

def wait(cb, numseconds = .5, *args, **kwargs):
    import datetime
    tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=numseconds), callback = lambda: cb(*args, **kwargs))

    print("waited")

def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            (r"/a/message/new", MessageNewHandler),
            (r"/a/action", ActionEventHandler),
            (r"/a/action/updates", ActionUpdateHandler),
            (r"/a/message/updates", MessageUpdatesHandler),
            (r"/test", TestHandler),
            (r"/a/loaded", LoadHandler),
            ],
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        login_url="/auth/login",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        debug = True,
        )
    app.listen(options.port)
    print("app started on port %s" %options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
